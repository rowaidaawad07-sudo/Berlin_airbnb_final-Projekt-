from sqlalchemy import create_engine

engine = create_engine("postgresql://postgres:postgres@localhost:5432/berlin_airbnb_final")

try:
    conn = engine.connect()
    print("✅ Connection successful")
    conn.close()
except Exception as e:
    print("❌ Error:", e)