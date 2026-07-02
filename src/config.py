from pathlib import Path

# =====================================
# Project Paths
# =====================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

RAW_DATA_FILE = RAW_DATA_DIR / "berlin_airbnb_sample.csv"

CLEANED_DATA_FILE = PROCESSED_DATA_DIR / "berlin_airbnb_cleaned.csv"

ML_DATA_FILE = PROCESSED_DATA_DIR / "berlin_airbnb_cleaned_ML.csv"

MODEL_DIR = BASE_DIR / "models"

MODEL_FILE = MODEL_DIR / "price_prediction_model.pkl"

SCALER_FILE = MODEL_DIR / "scaler.pkl"

ENCODER_FILE = MODEL_DIR / "label_encoders.pkl"

# =====================================
# Database
# =====================================

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/berlin_airbnb_final"