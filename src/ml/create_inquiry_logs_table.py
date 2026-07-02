import json
import sys
import psycopg2
from pathlib import Path

# ==========================
# Adding the project path to sys.path
# ==========================
current_file = Path(__file__).resolve()                # .../src/ml/create_inquiry_logs_table.py
project_root = current_file.parent.parent.parent       # .../berlin_airbnb_final
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# ==========================
# Importing config from src
# ==========================
try:
    from src.config import DATABASE_URL
    print("✅ Successfully imported DATABASE_URL from src.config")
except ImportError as e:
    print("❌ Failed to import src.config:", e)
    sys.exit(1)

# ==========================
# Path to training_metadata.json
# ==========================
metadata_path = current_file.parent / "training_metadata.json"
if not metadata_path.exists():
    print("❌ File training_metadata.json does not exist:", metadata_path)
    sys.exit(1)

with open(metadata_path, "r", encoding="utf-8") as f:
    metadata = json.load(f)

# Building the table columns
columns = []
for key, value in metadata.items():
    if isinstance(value, bool):
        col_type = "INTEGER"
    elif isinstance(value, int):
        col_type = "INTEGER"
    elif isinstance(value, float):
        col_type = "REAL"
    else:
        col_type = "VARCHAR(255)"
    columns.append(f'"{key}" {col_type}')

columns.append('"predicted_price" REAL')

# ==========================
# Creating the table
# ==========================
try:
    conn = psycopg2.connect(DATABASE_URL, client_encoding='UTF8')
    cursor = conn.cursor()
    create_query = f"""
    CREATE TABLE IF NOT EXISTS inquiry_logs (
        id SERIAL PRIMARY KEY,
        {', '.join(columns)}
    );
    """
    cursor.execute(create_query)
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ The table inquiry_logs has been created successfully!")
except Exception as e:
    print(f"❌ Failed to create the table: {e}")