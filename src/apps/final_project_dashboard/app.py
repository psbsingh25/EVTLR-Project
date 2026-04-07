"""Final Streamlit dashboard for Curry County wheat production systems."""

from __future__ import annotations

import base64
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


REPO_ROOT = Path(__file__).resolve().parents[3]
ASSETS_DIR = REPO_ROOT / "output" / "dashboard_assets"
NDVI_STATS_PATH = REPO_ROOT / "data" / "imagery" / "assignment-07" / "fields_with_mean_ndvi_soil.csv"


st.set_page_config(
    page_title="East New Mexico Wheat Production System",
    page_icon="🌾",
    layout="wide",
)


def image_exists(path: Path) -> bool:
    """Return True if the image exists."""

    return path.exists() and path.is_file()


def render_zoomable_image(image_path: Path, caption: str, element_id: str) -> None:
    """Render image with click-to-zoom modal using inline HTML."""

    if not image_exists(image_path):
        st.error(f"Missing asset: `{image_path}`")
        return

    encoded = base64.b64encode(image_path.read_bytes()).decode("utf-8")
    html = f"""
    <div id="wrap-{element_id}" style="margin: 0.25rem 0 1rem 0;">
      <img
        id="img-{element_id}"
        src="data:image/png;base64,{encoded}"
        alt="{caption}"
        style="width:100%; border:1px solid #d1d5db; border-radius:10px; cursor:zoom-in;"
      />
      <p style="font-size:0.9rem; color:#4b5563; margin-top:0.35rem;">{caption} (click image to zoom)</p>
    </div>
    <div id="modal-{element_id}" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.8); z-index:99999; align-items:center; justify-content:center; padding:2rem;">
      <div style="position:relative; max-width:96vw; max-height:94vh;">
        <button
          id="close-{element_id}"
          style="position:absolute; right:0; top:-2.25rem; padding:0.35rem 0.75rem; border-radius:6px; border:1px solid #fff; color:#fff; background:rgba(0,0,0,0.35); cursor:pointer;"
        >Close</button>
        <img
          src="data:image/png;base64,{encoded}"
          alt="{caption}"
          style="max-width:96vw; max-height:90vh; border-radius:8px; border:2px solid #fff;"
        />
      </div>
    </div>
    <script>
      (function() {{
        const image = document.getElementById("img-{element_id}");
        const modal = document.getElementById("modal-{element_id}");
        const closeButton = document.getElementById("close-{element_id}");
        image.addEventListener("click", () => {{
          modal.style.display = "flex";
        }});
        closeButton.addEventListener("click", () => {{
          modal.style.display = "none";
        }});
        modal.addEventListener("click", (event) => {{
          if (event.target === modal) modal.style.display = "none";
        }});
        document.addEventListener("keydown", (event) => {{
          if (event.key === "Escape") modal.style.display = "none";
        }});
      }})();
    </script>
    """
    components.html(html, height=700)


@st.cache_data
def load_ndvi_stats() -> pd.DataFrame:
    """Load Assignment 07 NDVI per-field stats."""

    if not NDVI_STATS_PATH.exists():
        return pd.DataFrame(
            columns=["field_id", "mean_ndvi", "ndvi_status", "soil_name", "drainage"]
        )

    frame = pd.read_csv(NDVI_STATS_PATH)
    curry = frame[frame["county"] == "Curry"].copy()
    curry["ndvi_status"] = curry["mean_ndvi"].apply(
        lambda value: "Low vegetation" if value < 0.3 else "Healthy-to-moderate"
    )
    return curry.sort_values("mean_ndvi")


def render_header() -> None:
    """Render dashboard heading and intro."""

    st.title("East New Mexico Wheat Production System")
    st.caption(
        "Final project dashboard combining Assignment 03-08 visuals, "
        "Curry-focused climate/NDVI interpretation, and AI narratives."
    )
    st.markdown(
        "Use the section navigator in the sidebar to move through crop area, "
        "productivity, weather trends, soil scorecard, and NDVI maps."
    )


def render_crop_section() -> None:
    """Render crop area section."""

    st.subheader("1) Total Crop Estimated Area (2020)")
    crop_path = ASSETS_DIR / "02_crop_total_estimated_area_2020.png"
    render_zoomable_image(
        crop_path,
        "2020 total estimated crop area by class",
        "crop2020",
    )
    st.info(
        "AI narrative: The 2020 acreage profile is concentrated in a few dominant "
        "crop classes, which suggests production risk is tied to a narrow crop mix. "
        "Diversifying crop classes can reduce exposure to weather and market shocks."
    )


def render_productivity_section() -> None:
    """Render productivity section."""

    st.subheader("2) Winter Wheat Productivity (Top 5 vs Bottom 5)")
    productivity_path = ASSETS_DIR / "wheat_productivity_top5_bottom5.png"
    render_zoomable_image(
        productivity_path,
        "Top five and bottom five winter wheat productivity fields",
        "productivity",
    )
    st.info(
        "AI narrative: The top-vs-bottom split highlights structural performance "
        "gaps across fields, likely tied to soil quality, water retention, and "
        "microclimate differences. Prioritize management interventions on the bottom "
        "group and benchmark them against top-field practices."
    )


def render_weather_section() -> None:
    """Render static weather trend section."""

    st.subheader("3) Curry County Weather Trends")
    weather_path = ASSETS_DIR / "weather_trends.png"
    render_zoomable_image(
        weather_path,
        "Curry County weather trends",
        "weathertrends",
    )

    st.info(
        "AI narrative: Curry County seasonal climate shows clear heat-pressure "
        "periods and variable rainfall intervals. Clusters of high smoothed "
        "temperature with low precipitation indicate stress windows where irrigation "
        "timing and heat-resilient practices have the highest payoff."
    )


def render_soil_section() -> None:
    """Render soil scorecard section."""

    st.subheader("4) Soil Health and Sustainability Scorecard")
    soil_path = ASSETS_DIR / "soil_health_metrics.png"
    render_zoomable_image(
        soil_path,
        "Soil health and sustainability scorecard",
        "soilscore",
    )
    st.info(
        "AI narrative: The scorecard surfaces differences in OM, pH suitability, "
        "and CEC-linked fertility behavior across counties. Use it as a management "
        "prioritization lens: fields with weaker composite profiles should be first "
        "for soil amendment and long-term resilience planning."
    )


def render_ndvi_section() -> None:
    """Render NDVI maps and alerts section."""

    st.subheader("5) Curry County NDVI Maps (2020-03-07)")
    combined_path = ASSETS_DIR / "integrated_spatial_analysis_curry_combined.png"
    render_zoomable_image(
        combined_path,
        "Combined Curry NDVI maps with field-level zoom panels",
        "ndvicombined",
    )

    ndvi = load_ndvi_stats()
    if ndvi.empty:
        st.warning(
            "NDVI field summary table is unavailable because the source NDVI CSV is missing. "
            "Maps are still shown from committed dashboard assets."
        )
        return

    low_ndvi = ndvi[ndvi["mean_ndvi"] < 0.3]

    st.markdown("**Curry field NDVI summary**")
    st.dataframe(
        ndvi[["field_id", "mean_ndvi", "ndvi_status", "soil_name", "drainage"]],
        use_container_width=True,
        hide_index=True,
    )

    if not low_ndvi.empty:
        st.warning(
            "NDVI alert: One or more Curry fields are below 0.3, indicating low "
            "vegetation vigor and potential crop stress. Prioritize scouting for "
            "water stress, nutrient limitations, and emergence gaps."
        )
        st.write("Flagged fields:", ", ".join(low_ndvi["field_id"].tolist()))
    else:
        st.success("All Curry NDVI values are at or above 0.3 for the selected date.")

    st.info(
        "AI narrative: Spatial NDVI contrasts show where canopy development is lagging "
        "inside Curry County. The NDVI threshold rule (< 0.3) is used as a rapid triage "
        "signal for low vegetation performance and targeted intervention."
    )


def main() -> None:
    """Run the final dashboard app."""

    render_header()

    sections = [
        "All sections",
        "1) Crop estimated area",
        "2) Wheat productivity",
        "3) Weather trends",
        "4) Soil scorecard",
        "5) NDVI maps and alerts",
    ]
    selected = st.sidebar.radio("Navigate sections", sections)

    if selected == "All sections":
        render_crop_section()
        render_productivity_section()
        render_weather_section()
        render_soil_section()
        render_ndvi_section()
    elif selected.startswith("1"):
        render_crop_section()
    elif selected.startswith("2"):
        render_productivity_section()
    elif selected.startswith("3"):
        render_weather_section()
    elif selected.startswith("4"):
        render_soil_section()
    else:
        render_ndvi_section()


if __name__ == "__main__":
    main()
