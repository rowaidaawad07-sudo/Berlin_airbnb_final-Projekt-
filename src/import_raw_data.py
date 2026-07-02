import pandas as pd

from database import engine
from config import RAW_DATA_FILE


def import_raw_dataset():

    print("=" * 50)
    print("IMPORTING RAW DATA")
    print("=" * 50)

    df = pd.read_csv(RAW_DATA_FILE)

    print(f"Rows : {len(df)}")
    print(f"Columns : {len(df.columns)}")

    df.to_sql(
        "airbnb_raw",
        con=engine,
        if_exists="replace",
        index=False
    )

    print("✅ Raw dataset imported successfully.")


if __name__ == "__main__":
    import_raw_dataset()