import json
import os

# Define file path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Put this in src/ml
METADATA_PATH = os.path.join(BASE_DIR, "training_metadata.json")

# 1. Load the file with the correct encoding
with open(METADATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# 2. Correct the malformed keys
corrected_data = {}
for key, value in data.items():
    # Replace the incorrect encoding (NeukÃ¶lln -> Neukölln)
    new_key = key.replace("Neuk\u00c3\u00b6lln", "Neukölln")  # Example
    new_key = new_key.replace("Sch\u00c3\u00b6neberg", "Schöneberg")
    new_key = new_key.replace("Wei\u00c3\u009fensee", "Weißensee")
    # ... add any other cases you see in the file
    corrected_data[new_key] = value

# 3. Save the file with UTF-8 encoding and direct writing of Arabic/German characters
with open(METADATA_PATH, "w", encoding="utf-8") as f:
    json.dump(corrected_data, f, ensure_ascii=False, indent=4)

print("✅ File corrected successfully!")