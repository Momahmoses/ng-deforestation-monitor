"""Azure config for Deforestation Monitor."""
import os

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
AZURE_ML_WORKSPACE = os.getenv("AZURE_ML_WORKSPACE", "")
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST", "")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN", "")
AZURE_MAPS_KEY = os.getenv("AZURE_MAPS_KEY", "")
