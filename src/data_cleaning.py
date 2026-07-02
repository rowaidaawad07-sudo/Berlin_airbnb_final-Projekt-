import pandas as pd
from pathlib import Path

# ======================
# Paths
# ======================
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_FILE = BASE_DIR / "data" / "raw" / "berlin_airbnb_sample.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "berlin_airbnb_cleaned.csv"


def run_data_cleaning():

    print("START CLEANING...")

    # Load data
    df = pd.read_csv(RAW_FILE)
    print(f"Original shape: {df.shape}")

    # ======================
    # Drop duplicates
    # ======================
    df = df.drop_duplicates()

    # Fill numeric missing
    df["Bathrooms"] = df["Bathrooms"].fillna(df["Bathrooms"].median())
    df["Bedrooms"] = df["Bedrooms"].fillna(df["Bedrooms"].median())

    # Fill categorical missing
    df["Postal Code"] = df["Postal Code"].fillna("Unknown")
    df["Host Response Time"] = df["Host Response Time"].fillna("Unknown")
    df["Host Response Rate"] = df["Host Response Rate"].fillna("Unknown")
    df["City"] = df["City"].fillna("Berlin")

    # ======================
    # Drop useless column
    # ======================
    if "Square Feet" in df.columns:
        df = df.drop(columns=["Square Feet"])

    # ======================
    # Fill missing values (text columns)
    # ======================
    fill_values = {
        "Listing Name": "No Name",
        "Host Name": "Unknown Host",
        "Comments": "No Comment",
        "Is Superhost": "f"
    }

    df.fillna(fill_values, inplace=True)

    # ======================
    # Convert ratings → numeric + median fill
    # ======================
    rating_cols = [
        "Overall Rating",
        "Accuracy Rating",
        "Cleanliness Rating",
        "Checkin Rating",
        "Communication Rating",
        "Location Rating",
        "Value Rating"
    ]

    for col in rating_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df[col] = df[col].fillna(df[col].median())

    # ======================
    # Clean Price
    # ======================
    if "Price" in df.columns:
        df["Price"] = df["Price"].astype(str).str.replace(r"[^\d.]", "", regex=True)
        df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
        df = df[df["Price"] > 0]

    # ======================
    # Save cleaned data
    # ======================
    df.to_csv(OUTPUT_FILE, index=False)

    print("DONE ✔")
    print(f"Final shape: {df.shape}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    run_data_cleaning()