import os
import csv
import json
import time
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
import google.generativeai as genai
from tqdm import tqdm

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY not found in .env")
    exit(1)

genai.configure(api_key=api_key)

# Configuration
SELECTED_EXPORTS_FILE = "selected_exports.txt"
BASE_IMG_DIR = "invoice_imgs"
LOG_FILE = "verification_errors.log"
MAX_WORKERS = 15 # Same concurrency as processing

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

csv_lock = threading.Lock()

def find_image_path(filename):
    """
    Searches for the image file in the subdirectories of invoice_imgs.
    Returns absolute path if found, None otherwise.
    """
    # We know the structure is invoice_imgs/testXX/filename
    # But the CSV only has filename. We can walk the directory.
    for root, dirs, files in os.walk(BASE_IMG_DIR):
        if filename in files:
            return os.path.join(root, filename)
    return None

def verify_invoice(row, image_path):
    """
    Verifies the extracted data against the image.
    Returns a dict with verification results.
    """
    max_retries = 3
    base_delay = 2
    
    # Construct a readable string of the data to verify
    data_str = json.dumps({k: v for k, v in row.items() if k not in ['filename', 'confidence_score', 'verification_notes', 'suggested_corrections']}, indent=2)

    prompt = f"""
    You are a Quality Control Expert. 
    I will provide an invoice image and the data that was extracted from it.
    
    Extracted Data:
    {data_str}
    
    Your Task:
    1. Compare the Extracted Data against the Image visually.
    2. Check SPECIFICALLY for:
       - Confusions between '8' and 'B', '0' and 'O' or 'D'.
       - Correctness of the Total Amount and Currency (USD vs others).
       - Correctness of the Date.
       - Correctness of the Company Name (ignoring suffixes like Inc, NV).
    
    Output JSON ONLY:
    {{
        "confidence_score": <number 0-100>,
        "verification_notes": "<short string explaining any discrepancies or confirming accuracy>",
        "suggested_corrections": {{ <field>: <correct_value> }} (or null if no corrections)
    }}
    
    If the data is 100% correct, suggested_corrections should be null (or empty object) and score should be 100.
    If the image is illegible, set score to 0 and note it.
    """
    
    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            response = model.generate_content([
                {'mime_type': 'image/jpeg', 'data': image_data},
                prompt
            ])
            
            text = response.text
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            
            result = json.loads(text)
            return result

        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(base_delay * (2 ** attempt))
            else:
                logging.error(f"Verification failed for {os.path.basename(image_path)}: {e}")
                return {
                    "confidence_score": 0,
                    "verification_notes": f"Verification failed: {str(e)}",
                    "suggested_corrections": None
                }

def process_single_row(row, fieldnames, writer, file_lock):
    """
    Process a single row, verification, and write to output CSV.
    """
    filename = row.get('filename')
    if not filename:
        row['confidence_score'] = 0
        row['verification_notes'] = "No filename in record"
        write_row(row, fieldnames, writer, file_lock)
        return

    image_path = find_image_path(filename)
    if not image_path:
        row['confidence_score'] = 0
        row['verification_notes'] = "Image file not found"
        write_row(row, fieldnames, writer, file_lock)
        return
        
    verification_result = verify_invoice(row, image_path)
    
    row['confidence_score'] = verification_result.get('confidence_score', 0)
    row['verification_notes'] = verification_result.get('verification_notes', "")
    corrections = verification_result.get('suggested_corrections')
    row['suggested_corrections'] = json.dumps(corrections) if corrections else ""
    
    write_row(row, fieldnames, writer, file_lock)
    time.sleep(0.5) # Rate verify

def write_row(row, fieldnames, writer, lock):
    with lock:
        writer.writerow(row)

def process_csv_file(csv_path):
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return

    output_path = csv_path.replace(".csv", "_verified.csv")
    print(f"Verifying {csv_path} -> {output_path}")
    
    rows = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames + ['confidence_score', 'verification_notes', 'suggested_corrections']
        rows = list(reader)
        
    if not rows:
        print("No rows to verify.")
        return

    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        file_lock = threading.Lock()
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(process_single_row, row, fieldnames, writer, file_lock) for row in rows]
            for _ in tqdm(as_completed(futures), total=len(rows), desc=f"Verifying {os.path.basename(csv_path)}"):
                pass

def main():
    if not os.path.exists(SELECTED_EXPORTS_FILE):
        print(f"{SELECTED_EXPORTS_FILE} not found.")
        return
        
    with open(SELECTED_EXPORTS_FILE, 'r') as f:
        files = [line.strip() for line in f if line.strip()]
        
    for csv_file in files:
        process_csv_file(csv_file)

if __name__ == "__main__":
    main()
