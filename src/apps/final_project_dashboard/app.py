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
NDVI_SUMMARY_FALLBACK_PATH = ASSETS_DIR / "curry_ndvi_summary.csv"


st.set_page_config(
    page_title="East New Mexico Wheat Production System",
    page_icon="🌾",
    layout="wide",
)


def image_exists(path: Path) -> bool:
    """Return True if the image exists."""

    return path.exists() and path.is_file()


def render_zoomable_image(
    image_path: Path,
    caption: str,
    element_id: str,
    component_height: int = 700,
) -> None:
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
    <div id="modal-{element_id}" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.85); z-index:99999; align-items:center; justify-content:center; padding:1rem;">
      <div style="position:relative; width:96vw; max-width:1700px;">
        <div style="position:absolute; right:0; top:-2.5rem; display:flex; gap:0.5rem;">
          <button id="zoom-in-{element_id}" style="padding:0.35rem 0.75rem; border-radius:6px; border:1px solid #fff; color:#fff; background:rgba(0,0,0,0.35); cursor:pointer;">+</button>
          <button id="zoom-out-{element_id}" style="padding:0.35rem 0.75rem; border-radius:6px; border:1px solid #fff; color:#fff; background:rgba(0,0,0,0.35); cursor:pointer;">-</button>
          <button id="zoom-reset-{element_id}" style="padding:0.35rem 0.75rem; border-radius:6px; border:1px solid #fff; color:#fff; background:rgba(0,0,0,0.35); cursor:pointer;">Reset</button>
          <button id="close-{element_id}" style="padding:0.35rem 0.75rem; border-radius:6px; border:1px solid #fff; color:#fff; background:rgba(0,0,0,0.35); cursor:pointer;">Close</button>
        </div>
        <div id="viewport-{element_id}" style="width:96vw; max-width:1700px; height:88vh; overflow:auto; border-radius:8px; border:2px solid #fff; background:#0b1220;">
          <img
            id="zoom-img-{element_id}"
            src="data:image/png;base64,{encoded}"
            alt="{caption}"
            style="display:block; width:min(1600px, 96vw); max-width:none; height:auto; transform:scale(1); transform-origin:top left; border-radius:6px;"
          />
        </div>
      </div>
    </div>
    <script>
      (function() {{
        const image = document.getElementById("img-{element_id}");
        const modal = document.getElementById("modal-{element_id}");
        const closeButton = document.getElementById("close-{element_id}");
        const zoomImage = document.getElementById("zoom-img-{element_id}");
        const viewport = document.getElementById("viewport-{element_id}");
        const zoomIn = document.getElementById("zoom-in-{element_id}");
        const zoomOut = document.getElementById("zoom-out-{element_id}");
        const zoomReset = document.getElementById("zoom-reset-{element_id}");
        let scale = 1;

        const setScale = (nextScale) => {{
          scale = Math.max(1, Math.min(4, nextScale));
          zoomImage.style.transform = `scale(${{scale}})`;
        }};

        image.addEventListener("click", () => {{
          setScale(1);
          modal.style.display = "flex";
        }});
        zoomIn.addEventListener("click", () => setScale(scale + 0.25));
        zoomOut.addEventListener("click", () => setScale(scale - 0.25));
        zoomReset.addEventListener("click", () => setScale(1));
        viewport.addEventListener("wheel", (event) => {{
          if (!modal || modal.style.display !== "flex") return;
          event.preventDefault();
          const delta = event.deltaY < 0 ? 0.15 : -0.15;
          setScale(scale + delta);
        }}, {{ passive: false }});
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
    components.html(html, height=component_height)


@st.cache_data
def load_ndvi_stats() -> pd.DataFrame:
    """Load Assignment 07 NDVI per-field stats."""

    columns = ["field_id", "mean_ndvi", "ndvi_status", "soil_name", "drainage"]
    if NDVI_SUMMARY_FALLBACK_PATH.exists():
        curry = pd.read_csv(NDVI_SUMMARY_FALLBACK_PATH)
    elif NDVI_STATS_PATH.exists():
        frame = pd.read_csv(NDVI_STATS_PATH)
        curry = frame[frame["county"] == "Curry"].copy()
    else:
        return pd.DataFrame(columns=columns)

    for required in ["field_id", "mean_ndvi", "soil_name", "drainage"]:
        if required not in curry.columns:
            curry[required] = ""

    curry["mean_ndvi"] = pd.to_numeric(curry["mean_ndvi"], errors="coerce")
    curry = curry.dropna(subset=["mean_ndvi"]).copy()
    curry["ndvi_status"] = curry["mean_ndvi"].apply(
        lambda value: "Low vegetation" if value < 0.3 else "Healthy-to-moderate"
    )
    return curry[columns].sort_values("mean_ndvi")


def render_sidebar_branding() -> None:
    """Render sidebar branding visuals for New Mexico context."""

    st.sidebar.markdown(
        """
        <div style="padding:0.35rem 0 0.75rem 0;">
          <svg viewBox="0 0 220 170" width="100%" aria-label="New Mexico map">
            <path d="M48 20 L172 20 L172 138 L48 138 L48 20 Z" fill="#f4e4bc" stroke="#5b2d0d" stroke-width="4" />
            <path d="M48 54 L66 54 L66 70 L84 70 L84 86 L110 86 L110 98 L172 98" fill="none" stroke="#8a4b16" stroke-width="4" />
            <text x="110" y="88" text-anchor="middle" fill="#c1121f" font-size="42" font-weight="700" font-family="Georgia, serif">NM</text>
          </svg>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    """Render dashboard heading and intro."""

    st.title("East New Mexico Wheat Production System")
    st.caption(
        "Final project dashboard combining Assignment 03-08 visuals, "
        "Curry-focused climate/NDVI interpretation, and decision-focused insights."
    )
    st.markdown(
        "East New Mexico is the home of New Mexico Dairy and related "
        "livestock-cropping systems. Winter wheat is an important irrigated "
        "and dryland crop of this region."
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
        "The 2020 acreage profile is concentrated in a few dominant "
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
        "The top-vs-bottom split highlights structural performance "
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
        component_height=1200,
    )

    st.info(
        "Curry County seasonal climate shows clear heat-pressure "
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
        "The scorecard surfaces differences in OM, pH suitability, "
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
            "NDVI field summary table is unavailable because the source NDVI files are "
            "missing from this environment. Maps are still shown from committed dashboard "
            "assets."
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
        "These three are the top wheat-producing fields in Curry County, New Mexico. "
        "As we can see, all three fields have an NDVI index below 0.4, which indicates "
        "that wheat crops are under stress. This is common in this part of the country, "
        "as water resources are diminishing and farmers are increasingly forced to "
        "deficit-irrigate their fields."
    )


def main() -> None:
    """Run the final dashboard app."""

    render_sidebar_branding()

    st.sidebar.markdown(
        "<div style='height:1rem;'></div>",
        unsafe_allow_html=True,
    )

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

    st.sidebar.markdown(
        "<div style='position:relative; margin-top:2rem; color:#8b1d1d; font-weight:700;'>"
        "🌶️ New Mexico Chile"
        "</div>",
        unsafe_allow_html=True,
    )

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
