"""Final Streamlit dashboard for Curry County wheat production systems."""

from __future__ import annotations

import base64
import json
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


REPO_ROOT = Path(__file__).resolve().parents[3]
ASSETS_DIR = REPO_ROOT / "output" / "dashboard_assets"
WEATHER_PATH = REPO_ROOT / "data" / "weather" / "nm_weather_2005_2020.csv"
FIELDS_PATH = REPO_ROOT / "data" / "boundaries" / "nm_top_200_fields.geojson"
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
def load_field_county_lookup() -> dict[str, str]:
    """Load field to county mapping from GeoJSON."""

    payload = json.loads(FIELDS_PATH.read_text(encoding="utf-8"))
    return {
        feature["properties"]["field_id"]: feature["properties"]["county"]
        for feature in payload["features"]
    }


@st.cache_data
def load_weather_trends() -> pd.DataFrame:
    """Load and aggregate Curry weather trend data."""

    weather = pd.read_csv(WEATHER_PATH, parse_dates=["date"])
    county_lookup = load_field_county_lookup()
    weather["county"] = weather["field_id"].map(county_lookup)
    curry = weather[weather["county"] == "Curry"].copy()

    curry["high_f"] = (curry["T2M_MAX"] * 9 / 5) + 32
    grouped = (
        curry.groupby("date", as_index=False)
        .agg(
            high_f=("high_f", "mean"),
            precip_mm=("PRECTOTCORR", "mean"),
        )
        .sort_values("date")
    )
    grouped["high_f_roll15"] = grouped["high_f"].rolling(15, min_periods=1).mean()
    grouped["precip_roll15"] = grouped["precip_mm"].rolling(15, min_periods=1).mean()
    grouped["is_heat_alert"] = grouped["high_f_roll15"] > 105
    return grouped


@st.cache_data
def load_ndvi_stats() -> pd.DataFrame:
    """Load Assignment 07 NDVI per-field stats."""

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
    """Render weather trend section."""

    st.subheader("3) Curry County Weather Trends")
    weather = load_weather_trends()

    min_date = weather["date"].min().date()
    max_date = weather["date"].max().date()
    selected_dates = st.slider(
        "Date range",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="YYYY-MM-DD",
    )

    subset = weather[
        (weather["date"].dt.date >= selected_dates[0])
        & (weather["date"].dt.date <= selected_dates[1])
    ].copy()

    st.markdown("**15-day smoothed maximum temperature (F)**")
    st.line_chart(subset.set_index("date")["high_f_roll15"], height=260)

    st.markdown("**15-day smoothed precipitation (mm)**")
    st.line_chart(subset.set_index("date")["precip_roll15"], height=260)

    heat_days = int(subset["is_heat_alert"].sum())
    st.metric("Heat-alert days (15-day avg > 105F)", heat_days)

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

    col1, col2, col3 = st.columns(3)
    with col1:
        render_zoomable_image(
            ASSETS_DIR / "integrated_spatial_analysis_curry_nm_field_019.png",
            "Curry NM_FIELD_019 NDVI map",
            "ndvi019",
        )
    with col2:
        render_zoomable_image(
            ASSETS_DIR / "integrated_spatial_analysis_curry_nm_field_060.png",
            "Curry NM_FIELD_060 NDVI map",
            "ndvi060",
        )
    with col3:
        render_zoomable_image(
            ASSETS_DIR / "integrated_spatial_analysis_curry_nm_field_188.png",
            "Curry NM_FIELD_188 NDVI map",
            "ndvi188",
        )

    ndvi = load_ndvi_stats()
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
