import sys
import os

# Adding the current directory to paths so Python can see the 'src' folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.cleaning.clean_data import run_data_cleaning
from src.modeling.create_tables import build_relational_tables

if __name__ == "__main__":
    print("🚀 Starting data pipeline execution...")
    try:
        run_data_cleaning()       # Step 1
        build_relational_tables()  # Step 2
        print("🎉 Data pipeline executed successfully!")
    except Exception as e:
        print(f"❌ An error occurred during execution: {e}")