# 🌳 Nigeria Deforestation & Land Degradation Monitor

Satellite-data-driven forest monitoring platform tracking Nigeria's deforestation across 20 forest states from 2000–2023, using **GIS change detection**, **PySpark**, **Azure ML**, and **Streamlit**.

## Problem Statement
Nigeria loses ~350,000 hectares annually — one of the world's worst deforestation rates. The Niger Delta and Cross River rainforests are critically threatened. This platform monitors forest cover loss, carbon stock changes, and deforestation drivers to support REDD+ policy decisions.

## Quick Start
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data Sources (Production)
- **Global Forest Watch (Hansen)** — Annual tree cover loss rasters
- **Sentinel-2** — NDVI time series
- **ESA CCI Land Cover** — Annual land cover classification
- **NESREA** — National Environmental Standards Agency
