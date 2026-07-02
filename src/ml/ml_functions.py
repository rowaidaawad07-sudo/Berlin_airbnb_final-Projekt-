import json
import requests
import re
import os
import time
from langdetect import detect

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
METADATA_PATH = os.path.join(BASE_DIR, "training_metadata.json")

with open(METADATA_PATH, "r", encoding="utf-8") as f:
    training_metadata = json.load(f)

# ==========================
# Clean Email Text (Remove Headers)
# ==========================
def clean_email_text(text):
    """Remove email headers (From:, Date:, Subject:, etc.) and keep the actual message."""
    lines = text.split('\n')
    cleaned_lines = []
    in_header = True
    for line in lines:
        if in_header:
            # Check if line is a header (starts with common header patterns)
            if re.match(r'^(From|Date|Subject|To|CC|BCC|Reply-To|Message-ID|In-Reply-To|References|MIME-Version|Content-Type|Content-Transfer-Encoding|X-|Return-Path|Received|Delivered-To|Authentication-Results|DKIM-Signature|DomainKey-Signature|Feedback-ID|List-|Thread-|Precedence|Errors-To|Sender|Importance|Sensitivity|X-|ARC-|BIMI-|MIME-|Content-|Message-):', line, re.IGNORECASE):
                continue  # Skip header lines
            elif line.strip() == '':
                # Blank line indicates end of headers
                in_header = False
                continue
            else:
                # If not a header and not blank, it's the start of the body
                in_header = False
                cleaned_lines.append(line.strip())
        else:
            cleaned_lines.append(line.strip())
    
    # Join and clean extra whitespace
    cleaned_text = '\n'.join([line for line in cleaned_lines if line.strip()])
    return cleaned_text

# ==========================
# Direct Extraction (Regex)
# ==========================
def extract_directly(text):
    """Extract data directly using regex (supports English & German)."""
    data = {}
    
    # Clean the text first
    clean_text = clean_email_text(text)
    
    # Try to find numbers
    accomodates = re.search(r'(\d+)\s*guests?', clean_text, re.IGNORECASE)
    if not accomodates:
        accomodates = re.search(r'(\d+)\s*Gäste', clean_text)
    if not accomodates:
        accomodates = re.search(r'accommodates?\s*(\d+)', clean_text, re.IGNORECASE)
    if accomodates:
        data['Accomodates'] = int(accomodates.group(1))
    
    bedrooms = re.search(r'(\d+)\s*bedrooms?', clean_text, re.IGNORECASE)
    if not bedrooms:
        bedrooms = re.search(r'(\d+)\s*Schlafzimmer', clean_text)
    if bedrooms:
        data['Bedrooms'] = int(bedrooms.group(1))
    
    bathrooms = re.search(r'(\d+)\s*bathrooms?', clean_text, re.IGNORECASE)
    if not bathrooms:
        bathrooms = re.search(r'(\d+)\s*Badezimmer', clean_text)
    if bathrooms:
        data['Bathrooms'] = int(bathrooms.group(1))
    
    beds = re.search(r'(\d+)\s*beds?', clean_text, re.IGNORECASE)
    if not beds:
        beds = re.search(r'(\d+)\s*Betten', clean_text)
    if beds:
        data['Beds'] = int(beds.group(1))
    
    # Keywords
    data['Is Superhost_t'] = 1 if re.search(r'Superhost', clean_text, re.IGNORECASE) else 0
    data['Instant Bookable_t'] = 1 if re.search(r'instant(ly)?\s*book|book\s*instantly|sofort\s*buch', clean_text, re.IGNORECASE) else 0
    
    # Neighbourhood
    neighbourhood = None
    clean_text = text.strip()
    
    # 1. Look for "Berlin-NAME" or "Berlin NAME" (most common pattern)
    #    Example: "Berlin-Mitte", "Berlin Charlottenburg"
    match = re.search(r'Berlin[-\s]+([A-Za-zäöüß]+)', clean_text, re.IGNORECASE)
    if match:
        candidate = match.group(1).strip()
        # Check if it's a known neighbourhood (optional)
        known = ['Neukölln', 'Mitte', 'Kreuzberg', 'Prenzlauer Berg', 'Charlottenburg',
                 'Friedrichshain', 'Schöneberg', 'Tempelhof', 'Tiergarten', 'Moabit']
        for hood in known:
            if candidate.lower() == hood.lower() or candidate.lower() in hood.lower():
                neighbourhood = candidate
                break
        # If not in known list, still keep it as it might be a valid name
        if not neighbourhood:
            neighbourhood = candidate
    
    # 2. If not found, search for known neighbourhood names directly in text
    if not neighbourhood:
        known_neighbourhoods = ['Neukölln', 'Mitte', 'Kreuzberg', 'Prenzlauer Berg', 'Charlottenburg',
                                'Friedrichshain', 'Schöneberg', 'Tempelhof', 'Tiergarten', 'Moabit']
        for hood in known_neighbourhoods:
            if hood.lower() in clean_text.lower():
                neighbourhood = hood
                break
    
    if neighbourhood:
        data['Neighbourhood'] = neighbourhood
        print(f"📍 Neighbourhood extracted: {neighbourhood}")
    
    return data

# ==========================
# Ollama Extraction
# ==========================
def try_extract_with_ollama(email_text, max_retries=2):
    """Extract using Ollama with cleaned text."""
    print("\n==============================")
    print("Starting Ollama Extraction")
    print("==============================")

    # Clean the text to remove headers
    cleaned_text = clean_email_text(email_text)
    print(f"Cleaned text length: {len(cleaned_text)} characters")

    prompt = f"""
You are an AI assistant that extracts structured data from Airbnb inquiry emails.

Extract these fields from the email message below:
- "Accomodates": number of guests (integer)
- "Bedrooms": number of bedrooms (integer)
- "Bathrooms": number of bathrooms (integer)
- "Beds": number of beds (integer)
- "Is Superhost_t": 1 if host is described as "Superhost", else 0
- "Instant Bookable_t": 1 if "instant booking" or "book instantly" is mentioned, else 0
- "Neighbourhood": the neighbourhood name from phrases like "in Berlin-Mitte", "in Mitte", or "in Neukölln"

Email message:
{cleaned_text}

Return ONLY valid JSON in this exact format, no additional text:
{{
    "Accomodates": 0,
    "Bedrooms": 0,
    "Bathrooms": 0,
    "Beds": 0,
    "Is Superhost_t": 0,
    "Instant Bookable_t": 0,
    "Neighbourhood": ""
}}
"""

    for attempt in range(1, max_retries + 1):
        print(f"\nAttempt {attempt}/{max_retries}")
        try:
            start = time.time()
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2:1b",
                    "prompt": prompt,
                    "stream": False,
                    "keep_alive": "10m",
                    "options": {
                        "temperature": 0.0,
                        "num_ctx": 2048,   # Larger context for full text
                        "num_predict": 150
                    }
                },
                timeout=600   # 10 minutes timeout
            )
            elapsed = time.time() - start
            print(f"Status Code: {response.status_code}")
            print(f"Time: {elapsed:.2f} seconds")

            if response.status_code != 200:
                print("Request failed")
                continue

            result = response.json()
            if "error" in result:
                print(f"Ollama Error: {result['error']}")
                continue

            raw = result.get("response", "").strip()
            if not raw:
                print("Empty response")
                continue

            print("Response:")
            print(raw[:300])

            raw = raw.replace("```json", "").replace("```", "").strip()

            try:
                extracted = json.loads(raw)
                print("\nJSON Parsed Successfully")
                for k, v in extracted.items():
                    print(f"{k}: {v}")
                return extracted
            except json.JSONDecodeError:
                match = re.search(r'\{.*\}', raw, re.DOTALL)
                if match:
                    try:
                        extracted = json.loads(match.group())
                        print("JSON extracted via Regex")
                        return extracted
                    except:
                        pass
                print("Failed to parse JSON")

        except requests.exceptions.Timeout:
            print("Timeout")
        except requests.exceptions.ConnectionError:
            print("Cannot connect to Ollama")
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")

    print("\nOllama extraction failed")
    return None

# ==========================
# Main Extraction Function
# ==========================
def extract_and_transform(email_text):
    """Extract features using Ollama, then fallback to regex."""
    extracted = None
    source = "default"

    # Try Ollama first
    extracted = try_extract_with_ollama(email_text)
    if extracted:
        source = "ollama"
        print("Extraction via Ollama successful")
    else:
        print("Ollama failed, using regex fallback")

    # Always get regex data to fill missing fields
    regex_data = extract_directly(email_text)
    if regex_data:
        print("Regex data extracted for fallback")

    # Merge: Ollama takes priority, but regex fills missing fields
    if extracted and regex_data:
        for key in ['Accomodates', 'Bedrooms', 'Bathrooms', 'Beds']:
            if extracted.get(key, 0) == 0 and regex_data.get(key, 0) > 0:
                extracted[key] = regex_data[key]
                print(f"Filled {key} from regex: {regex_data[key]}")
        if not extracted.get('Neighbourhood') and regex_data.get('Neighbourhood'):
            extracted['Neighbourhood'] = regex_data['Neighbourhood']
            print(f"Neighbourhood filled from regex: {regex_data['Neighbourhood']}")

    if not extracted and regex_data:
        extracted = regex_data
        source = "regex"
        print("Using regex extraction only")

    if not extracted:
        print("All methods failed, using default values")
        return training_metadata.copy()

    print("\n========== Extracted Values ==========")
    print(f"Source: {source}")
    for key, value in extracted.items():
        print(f"   {key}: {value}")
    print("======================================\n")

    data = training_metadata.copy()
    data.update(extracted)

    neighbourhood = extracted.get("Neighbourhood")
    if neighbourhood:
        col_name = f"neighbourhood_{neighbourhood}"
        if col_name in data:
            data[col_name] = 1
        coords = {
            "Neukölln": (52.4815, 13.4351),
            "Mitte": (52.5200, 13.4050),
            "Kreuzberg": (52.4986, 13.4035),
            "Prenzlauer Berg": (52.5380, 13.4240),
            "Charlottenburg": (52.5160, 13.3041)
        }
        if neighbourhood in coords:
            data["Latitude"], data["Longitude"] = coords[neighbourhood]

    return data

# ==========================
# Generate AI Reply
# ==========================
def get_ai_reply(email_text, price):
    """Generate reply using Ollama."""
    try:
        lang = detect(email_text)
    except:
        lang = "en"

    cleaned_text = clean_email_text(email_text)
    short_text = cleaned_text[:300] if len(cleaned_text) > 300 else cleaned_text

    if lang.startswith('de'):
        prompt = f"Airbnb-Assistent. Anfrage: {short_text} Preis: {price:.2f} EUR. Schreibe eine kurze, professionelle Antwort auf Deutsch."
    else:
        prompt = f"Airbnb assistant. Message: {short_text} Price: {price:.2f} EUR. Write a short, professional reply."

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:1b",
                "prompt": prompt,
                "stream": False,
                "temperature": 0.1,
                "options": {
                    "num_ctx": 256,
                    "num_predict": 150,
                    "keep_alive": "10m"
                }
            },
            timeout=300
        )
        result = response.json().get("response", "")
        return result if result else f"Estimated price: {price:.2f} EUR"
    except Exception as e:
        print(f"Error generating reply: {e}")
        return f"Estimated price: {price:.2f} EUR"