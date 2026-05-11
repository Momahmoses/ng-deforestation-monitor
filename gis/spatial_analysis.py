"""GIS: Deforestation hotspots, NDVI change, protected area proximity."""
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import folium
from folium.plugins import HeatMap
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.generate_data import generate_deforestation_events, generate_protected_areas, FOREST_STATES


def build_deforestation_map(events_df, protected_df, land_cover_df) -> folium.Map:
    m = folium.Map(location=[6.5, 7.0], zoom_start=6, tiles="CartoDB positron")

    heat = [[r.lat, r.lon, min(1.0, r.area_lost_ha / 2000)] for _, r in events_df.iterrows()]
    HeatMap(heat, radius=18, blur=15, min_opacity=0.4,
            gradient={"0.3": "yellow", "0.6": "orange", "1.0": "darkred"}).add_to(m)

    # 2023 forest cover circles
    latest = land_cover_df[land_cover_df["year"] == 2023]
    for _, row in latest.iterrows():
        cover = row["forest_cover_pct"] / 100
        color = "#1b5e20" if cover > 0.5 else "#f9a825" if cover > 0.3 else "#d32f2f"
        folium.CircleMarker(
            location=[row.lat, row.lon],
            radius=max(6, cover * 20),
            color=color, fill=True, fill_opacity=0.6,
            popup=(f"<b>{row['state']}</b><br>"
                   f"Forest Cover: {row['forest_cover_pct']:.1f}%<br>"
                   f"NDVI: {row['ndvi_mean']:.3f}"),
            tooltip=row["state"],
        ).add_to(m)

    # Protected areas
    for _, pa in protected_df.iterrows():
        folium.Marker(
            location=[pa.lat, pa.lon],
            popup=f"<b>{pa['name']}</b><br>{pa['area_km2']:,} km²<br>Status: {pa['status']}",
            icon=folium.Icon(color="green" if pa["status"] == "Active" else "red",
                             icon="tree", prefix="fa"),
        ).add_to(m)
    return m


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from data.generate_data import generate_land_cover_time_series
    events = generate_deforestation_events()
    protected = generate_protected_areas()
    land_cover = generate_land_cover_time_series()
    m = build_deforestation_map(events, protected, land_cover)
    os.makedirs("app", exist_ok=True)
    m.save("app/deforestation_map.html")
    print("Map saved.")
