import pandas as pd
import numpy as np
import os

FOREST_STATES = [
    ("Cross River", 5.9631, 8.3305, "Rainforest", 0.82),
    ("Edo", 6.3350, 5.6037, "Rainforest", 0.68),
    ("Ondo", 7.0003, 5.0000, "Forest-Savanna", 0.55),
    ("Ekiti", 7.6218, 5.2311, "Forest-Savanna", 0.50),
    ("Osun", 7.5629, 4.5624, "Forest-Savanna", 0.42),
    ("Ogun", 6.9980, 3.4737, "Forest-Savanna", 0.45),
    ("Lagos", 6.5244, 3.3792, "Mangrove", 0.30),
    ("Delta", 5.5320, 5.8987, "Rainforest/Mangrove", 0.60),
    ("Rivers", 4.8156, 7.0498, "Mangrove", 0.55),
    ("Bayelsa", 4.7719, 6.0699, "Mangrove", 0.65),
    ("Akwa Ibom", 5.0527, 7.9335, "Mangrove/Rainforest", 0.58),
    ("Imo", 5.4527, 7.0201, "Rainforest", 0.50),
    ("Abia", 5.3671, 7.4948, "Rainforest", 0.52),
    ("Anambra", 6.2104, 6.9623, "Forest-Savanna", 0.38),
    ("Enugu", 6.4584, 7.5464, "Forest-Savanna", 0.40),
    ("Ebonyi", 6.2649, 8.0137, "Forest-Savanna", 0.43),
    ("Benue", 7.3369, 8.7404, "Guinea Savanna", 0.35),
    ("Plateau", 9.2182, 9.5179, "Guinea Savanna", 0.32),
    ("Taraba", 7.9993, 10.7741, "Guinea Savanna", 0.48),
    ("Adamawa", 9.3265, 12.3984, "Guinea Savanna", 0.38),
]

DEFORESTATION_DRIVERS = [
    "Agricultural Expansion", "Logging/Timber", "Charcoal Production",
    "Urban Expansion", "Mining", "Wildfire", "Fuelwood Collection"
]


def generate_land_cover_time_series() -> pd.DataFrame:
    np.random.seed(42)
    records = []
    years = range(2000, 2024)
    for state, slat, slon, veg_type, base_cover in FOREST_STATES:
        cover = base_cover
        for year in years:
            annual_loss = np.random.uniform(0.008, 0.025)
            cover = max(0.02, cover - annual_loss + np.random.normal(0, 0.005))
            records.append({
                "state": state, "lat": slat, "lon": slon,
                "veg_type": veg_type, "year": year,
                "forest_cover_pct": round(cover * 100, 2),
                "ndvi_mean": round(cover * 0.9 + np.random.normal(0, 0.02), 3),
                "biomass_tons_ha": round(cover * 180 + np.random.normal(0, 5), 1),
                "carbon_stock_tco2_ha": round(cover * 250 + np.random.normal(0, 8), 1),
                "area_km2": round(np.random.uniform(5000, 40000), 0),
            })
    return pd.DataFrame(records)


def generate_deforestation_events(n: int = 500) -> pd.DataFrame:
    np.random.seed(42)
    records = []
    for i in range(n):
        state_info = FOREST_STATES[np.random.randint(len(FOREST_STATES))]
        state, slat, slon, veg_type, base = state_info
        records.append({
            "event_id": f"DEF-{i+1:05d}",
            "state": state, "veg_type": veg_type,
            "year": int(np.random.randint(2010, 2024)),
            "lat": slat + np.random.uniform(-0.6, 0.6),
            "lon": slon + np.random.uniform(-0.6, 0.6),
            "driver": np.random.choice(DEFORESTATION_DRIVERS,
                      p=[0.35, 0.20, 0.15, 0.12, 0.08, 0.05, 0.05]),
            "area_lost_ha": round(np.random.exponential(500), 0),
            "carbon_lost_tco2": round(np.random.exponential(8000), 0),
            "ndvi_before": round(np.random.uniform(0.5, 0.85), 3),
            "ndvi_after": round(np.random.uniform(0.1, 0.35), 3),
        })
    return pd.DataFrame(records)


def generate_protected_areas() -> pd.DataFrame:
    return pd.DataFrame([
        {"name": "Cross River National Park", "state": "Cross River", "lat": 5.8, "lon": 9.0, "area_km2": 4000, "status": "Active"},
        {"name": "Okomu National Park", "state": "Edo", "lat": 6.27, "lon": 5.37, "area_km2": 191, "status": "Active"},
        {"name": "Gashaka-Gumti NP", "state": "Taraba", "lat": 7.35, "lon": 11.58, "area_km2": 6731, "status": "Active"},
        {"name": "Kamuku NP", "state": "Kaduna", "lat": 11.0, "lon": 5.9, "area_km2": 1121, "status": "Active"},
        {"name": "Yankari NP", "state": "Bauchi", "lat": 9.83, "lon": 10.40, "area_km2": 2244, "status": "Active"},
        {"name": "Niger Delta Mangroves", "state": "Delta", "lat": 5.45, "lon": 5.75, "area_km2": 9600, "status": "Degraded"},
    ])


def save_all(output_dir: str = "data"):
    os.makedirs(output_dir, exist_ok=True)
    generate_land_cover_time_series().to_csv(f"{output_dir}/land_cover.csv", index=False)
    generate_deforestation_events().to_csv(f"{output_dir}/deforestation_events.csv", index=False)
    generate_protected_areas().to_csv(f"{output_dir}/protected_areas.csv", index=False)
    print("Deforestation data generated.")


if __name__ == "__main__":
    save_all()
