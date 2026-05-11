"""Nigeria Deforestation & Land Degradation Monitor — Streamlit Dashboard"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from streamlit_folium import st_folium
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from data.generate_data import (generate_land_cover_time_series, generate_deforestation_events,
                                  generate_protected_areas)
from gis.spatial_analysis import build_deforestation_map

st.set_page_config(page_title="NG Deforestation Monitor", page_icon="🌳", layout="wide")
st.markdown("""<style>
.kpi{background:#1b5e20;color:white;padding:14px;border-radius:8px;text-align:center;}
.kpi-val{font-size:1.9rem;font-weight:700;}
.kpi-lbl{font-size:.8rem;opacity:.85;}
</style>""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    lc = generate_land_cover_time_series()
    ev = generate_deforestation_events(400)
    pa = generate_protected_areas()
    return lc, ev, pa


def main():
    lc_df, events_df, protected_df = load_data()

    with st.sidebar:
        st.title("🌳 Deforestation")
        st.caption("Nigeria Land Monitor")
        st.divider()
        year_range = st.slider("Year Range", 2000, 2023, (2010, 2023))
        driver_filter = st.multiselect("Deforestation Driver",
                                       events_df["driver"].unique().tolist(),
                                       default=events_df["driver"].unique().tolist())
        veg_filter = st.multiselect("Vegetation Type",
                                    lc_df["veg_type"].unique().tolist(),
                                    default=lc_df["veg_type"].unique().tolist())

    lc_filtered = lc_df[lc_df["year"].between(year_range[0], year_range[1]) &
                         lc_df["veg_type"].isin(veg_filter)]
    ev_filtered = events_df[(events_df["year"] >= year_range[0]) &
                             (events_df["year"] <= year_range[1]) &
                             events_df["driver"].isin(driver_filter)]

    st.title("🌳 Nigeria Deforestation & Land Degradation Monitor")
    st.caption("Forest cover tracking · Carbon stock · NDVI change · GIS + PySpark + Azure ML")
    st.divider()

    latest = lc_df[lc_df["year"] == 2023]
    earliest = lc_df[lc_df["year"] == 2000]
    avg_2023 = latest["forest_cover_pct"].mean()
    avg_2000 = earliest["forest_cover_pct"].mean()
    total_area_lost = ev_filtered["area_lost_ha"].sum()
    total_carbon_lost = ev_filtered["carbon_lost_tco2"].sum()

    c1, c2, c3, c4 = st.columns(4)
    for col, val, lbl in zip(
        [c1, c2, c3, c4],
        [f"{avg_2023:.1f}%", f"{avg_2000 - avg_2023:.1f}%",
         f"{total_area_lost/1e6:.2f}M ha", f"{total_carbon_lost/1e6:.1f}M tCO₂"],
        ["Avg Forest Cover (2023)", "Cover Lost Since 2000",
         "Total Area Deforested", "Carbon Emitted"]
    ):
        col.markdown(f'<div class="kpi"><div class="kpi-val">{val}</div>'
                     f'<div class="kpi-lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.divider()
    col_map, col_trend = st.columns([3, 2])

    with col_map:
        st.subheader("🗺 Deforestation Hotspots")
        m = build_deforestation_map(ev_filtered, protected_df, lc_df)
        st_folium(m, width=700, height=460)

    with col_trend:
        st.subheader("📉 Forest Cover Trend")
        selected_state = st.selectbox("Select State", sorted(lc_df["state"].unique()))
        state_trend = lc_filtered[lc_filtered["state"] == selected_state]
        fig_t = px.area(state_trend, x="year", y="forest_cover_pct",
                        color_discrete_sequence=["#2e7d32"],
                        labels={"forest_cover_pct": "Forest Cover (%)", "year": "Year"})
        fig_t.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                            margin=dict(l=0, r=0, t=5, b=0))
        st.plotly_chart(fig_t, use_container_width=True, key="trend")

    st.divider()
    col_driver, col_ndvi = st.columns(2)

    with col_driver:
        st.subheader("🪓 Deforestation by Driver")
        drv = ev_filtered.groupby("driver")["area_lost_ha"].sum().sort_values().reset_index()
        fig_d = px.bar(drv, x="area_lost_ha", y="driver", orientation="h",
                       color="area_lost_ha", color_continuous_scale="Reds",
                       labels={"area_lost_ha": "Area Lost (ha)", "driver": ""})
        fig_d.update_layout(coloraxis_showscale=False,
                            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                            margin=dict(l=0, r=0, t=5, b=0))
        st.plotly_chart(fig_d, use_container_width=True)

    with col_ndvi:
        st.subheader("📊 NDVI Before vs After Events")
        sample = ev_filtered.sample(min(100, len(ev_filtered)), random_state=42)
        fig_ndvi = px.scatter(sample, x="ndvi_before", y="ndvi_after",
                              color="driver", hover_name="state",
                              labels={"ndvi_before": "NDVI Before", "ndvi_after": "NDVI After"})
        fig_ndvi.add_shape(type="line", x0=0, y0=0, x1=1, y1=1,
                           line=dict(dash="dash", color="gray"))
        fig_ndvi.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                               margin=dict(l=0, r=0, t=5, b=0))
        st.plotly_chart(fig_ndvi, use_container_width=True)

    st.caption("Data: Synthetic — replace with Hansen Global Forest Watch, Sentinel-2, ESA CCI Land Cover. "
               "Pipeline: Azure Databricks PySpark + Azure ML pixel classification.")


if __name__ == "__main__":
    main()
