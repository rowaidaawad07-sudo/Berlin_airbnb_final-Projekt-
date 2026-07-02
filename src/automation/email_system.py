import os
import sys

# ==========================
# 1. Path Configuration
# ==========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))          # .../src/automation
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../../")) # .../berlin_airbnb_final

#Add the root to sys.path to enable imports from src
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ==========================
# 2.Modules can now be imported from src.
# ==========================
from src.ml.ml_functions import extract_and_transform, get_ai_reply
import src.ml.ml_functions as mf

print("=" * 60)
print("Using ml_functions from:")
print(mf.__file__)
print("=" * 60)

import imaplib
import email
import smtplib
import pandas as pd
import psycopg2
import time
import joblib
import warnings
warnings.filterwarnings("ignore")
from email.message import EmailMessage

# ==========================
# CONFIG
# ==========================
DB_CONFIG = "dbname=Berlin_Airbnb user=postgres password=postgres host=localhost port=5432"
EMAIL_USER = "E-mail@gmail.com"
EMAIL_PASS = "App Password"   # Use Gmail App Password

# ==========================
# 3. Model Paths within src/ml
# ==========================
ML_DIR = os.path.join(PROJECT_ROOT, "src", "ml")
MODEL_PATH = os.path.join(ML_DIR, "rf_model.pkl")
COLUMNS_PATH = os.path.join(ML_DIR, "model_columns.pkl")

print("⏳ Loading the model...")
try:
    model = joblib.load(MODEL_PATH)
    training_columns = joblib.load(COLUMNS_PATH)
    print("✅ Model and columns loaded successfully")
except Exception as e:
    print(f"❌ Failed to load the model: {e}")
    sys.exit(1)

# ==========================
# FUNCTIONS
# ==========================
def get_email_text(msg):
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get_content_disposition())
            if content_type == "text/plain" and "attachment" not in content_disposition:
                payload = part.get_payload(decode=True)
                return payload.decode(errors="ignore") if payload else ""
        return ""
    else:
        payload = msg.get_payload(decode=True)
        return payload.decode(errors="ignore") if payload else ""

def save_to_db(full_data):
    try:
        conn = psycopg2.connect(DB_CONFIG, client_encoding='UTF8')
        cursor = conn.cursor()
        
        # Fetch the column names existing in the table 
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'inquiry_logs'
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        # Filter the data so it only contains the existing columns
        filtered_data = {}
        for key, value in full_data.items():
            if key in existing_columns:
                filtered_data[key] = value
        
        # Convert booleans to integers
        for key, value in filtered_data.items():
            if isinstance(value, bool):
                filtered_data[key] = 1 if value else 0
        
        cols = ', '.join([f'"{col}"' for col in filtered_data.keys()])
        placeholders = ', '.join(['%s'] * len(filtered_data))
        query = f"INSERT INTO inquiry_logs ({cols}) VALUES ({placeholders})"
        cursor.execute(query, tuple(filtered_data.values()))
        conn.commit()
        cursor.close()
        conn.close()
        print("💾 Successfully saved to the database")
    except Exception as e:
        print(f"❌ Failed to save: {e}")
        import traceback
        traceback.print_exc()

def send_email(to_email, body):
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = "Re: Your Airbnb Inquiry"
        msg["From"] = EMAIL_USER
        msg["To"] = to_email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
        print("📤 Successfully sent the reply")
    except Exception as e:
        print(f"❌ Failed to send: {e}")

def run_system():
    print("🚀 Email automation system started...")
    while True:
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(EMAIL_USER, EMAIL_PASS)
            mail.select("inbox")
            _, unseen_ids = mail.search(None, "UNSEEN")
            unseen_list = unseen_ids[0].split()
            print(f"📨 Count the new messages: {len(unseen_list)}")

            for msg_id in unseen_list:
                try:
                    print(f"\n🔄 Processing email: {msg_id.decode()}")
                    _, data = mail.fetch(msg_id, "(RFC822)")
                    msg = email.message_from_bytes(data[0][1])
                    email_text = get_email_text(msg)

                    if not email_text:
                        mail.store(msg_id, '+FLAGS', '\\Seen')
                        continue

                    print("⏳ Loading features...")
                    full_data = extract_and_transform(email_text)

                    if full_data is None:
                        print("❌ Failed to extract features, skipping.")
                        mail.store(msg_id, '+FLAGS', '\\Seen')
                        continue

                    # ==========================
                    # Preparing the DataFrame
                    # ==========================
                    X_new = pd.DataFrame([full_data])
                    X_new = X_new.reindex(columns=training_columns, fill_value=0)

                    # Ensure all values are numeric
                    for col in X_new.columns:
                        if X_new[col].dtype == 'object':
                            X_new[col] = pd.to_numeric(X_new[col], errors='coerce').fillna(0)

                    # ==========================
                    # predicting the price
                    # ==========================
                    predicted_price = model.predict(X_new)[0]
                    print(f"💰 The predicted price: {predicted_price:.2f} EUR")

                    full_data["predicted_price"] = float(predicted_price)

                    # ==========================
                    # Saving to the database
                    # ==========================
                    save_to_db(full_data)

                    # ==========================
                    # Generating the smart reply
                    # ==========================
                    reply = get_ai_reply(email_text, predicted_price)
                    print("✅ Smart reply generated")

                    # ==========================
                    # Sending the reply
                    # ==========================
                    send_email(msg.get("From"), reply)

                    mail.store(msg_id, '+FLAGS', '\\Seen')
                    print("✅ Processing completed successfully")

                except Exception as e:
                    print(f"❌ Error processing email {msg_id}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue

            mail.logout()
            print("📤 Connection terminated")

        except Exception as e:
            print(f"❌ Error in main loop: {e}")
            import traceback
            traceback.print_exc()

        print("⏳ Waiting 60 seconds...")
        time.sleep(60)

if __name__ == "__main__":
    run_system()