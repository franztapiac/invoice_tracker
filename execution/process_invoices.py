import os
import csv
import json
import glob
import time
import re
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
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
BATCHES_FILE = "batches.txt"
BASE_INPUT_DIR = "receipt_imgs"
FIELDNAMES = ['date', 'company', 'invoice_number', 'amount', 'currency', 'filename']
LOG_FILE = "processing_errors.log"

# Rate Limiting configuration
# Quota: 1000 RPM (Requests Per Minute)
# Safe target: ~800 RPM to be safe => ~13 requests/sec
# With 10 threads, each thread needs to take >0.7s per request on average to stay safe.
# Actually, API latency is usually >1s, so 15-20 threads is likely safe.
MAX_WORKERS = 15  

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

csv_lock = threading.Lock()

def get_latest_batch_id():
    """
    Parses batches.txt to find the latest Batch ID.
    Returns the batch ID string (e.g., "02") or None if not found.
    """
    if not os.path.exists(BATCHES_FILE):
        print(f"Error: {BATCHES_FILE} not found.")
        return None

    try:
        with open(BATCHES_FILE, 'r') as f:
            content = f.read()
        
        # Regex to find all "Batch XX" headers
        matches = re.findall(r'Batch\s+(\d+)', content)
        
        if matches:
            # Return the last one found
            return matches[-1]
        else:
            return None
    except Exception as e:
        print(f"Error reading {BATCHES_FILE}: {e}")
        return None

def extract_invoice_data(image_path):
    """
    Uploads an image to Gemini and extracts invoice details.
    Includes retry logic and error logging.
    """
    max_retries = 3
    base_delay = 2
    
    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            with open(image_path, "rb") as f:
                image_data = f.read()
                
            prompt = """
            Analyze this invoice image and extract the following details in JSON format.
            
            Extraction Rules:
            1. **Company**: Extract the common trading name of the company. 
               - Remove legal suffixes like 'Inc', 'N.V.', 'B.V.', 'Ltd', 'S.A.', etc. (e.g., 'Island Water World Inc N.V' -> 'Island Water World').
               - If the logo/name is covered (e.g. by a receipt), look elsewhere in the document (headers, footers) for the company name.
            2. **Invoice Number**: Extract the invoice number (sometimes called 'slip #', 'bill #', 'sale no.', etc.).
            3. **Date**: Extract the date in YYYY-MM-DD format.
            4. **Total Amount & Currency**:
               - Look for the TOTAL amount.
               - **CRITICAL**: If the amount is available in USD and another currency (e.g., NAF, ANG, XCG, EUR), YOU MUST extract the USD amount and set currency to 'USD'.
               - Only use a different currency if USD is strictly NOT present. Do not calculate the USD amount.
               - Look throughout the whole image for currency codes/symbols if not immediately next to the total.
               
            Return ONLY the JSON object with these keys:
            - date (YYYY-MM-DD or null)
            - company (string or null)
            - invoice_number (string or null)
            - amount (number or null)
            - currency (string or null)
            """
            
            response = model.generate_content([
                {'mime_type': 'image/jpeg', 'data': image_data},
                prompt
            ])
            
            # Parse JSON from response
            text = response.text
            # Clean up code blocks if present
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            
            data = json.loads(text)
            
            # Basic validation: check if it's a dict
            if not isinstance(data, dict):
                raise ValueError("Response is not a JSON object")

            return data

        except Exception as e:
            if attempt < max_retries - 1:
                sleep_time = base_delay * (2 ** attempt)
                time.sleep(sleep_time)
                continue
            else:
                logging.error(f"Failed to process {os.path.basename(image_path)}: {str(e)}")
                return None

def process_single_image(img_path, output_file, existing_fieldnames):
    """
    Wrapper function to process a single image and write to CSV immediately (thread-safe).
    """
    try:
        data = extract_invoice_data(img_path)
        
        if data:
            data['filename'] = os.path.basename(img_path)
            
            with csv_lock:
                with open(output_file, 'a', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=existing_fieldnames)
                    writer.writerow(data)
                    csvfile.flush()
            return True # Success
        else:
            return False # Failed extraction (logged elsewhere)
            
    except Exception as e:
        logging.error(f"Wrapper failed for {os.path.basename(img_path)}: {str(e)}")
        return False

def main():
    batch_id = get_latest_batch_id()
    if not batch_id:
        print("Could not determine Batch ID from batches.txt.")
        return

    input_dir = os.path.join(BASE_INPUT_DIR, f"batch{batch_id}")
    
    # Generate output filename: exports/invoices_batch02_2026jan31_14;02.csv
    # NOTE: We keep the same filename format logic, but since we restart, we might want to checks for existing recent files
    # For now, let's look for the most recent existing file for this batch to append to, OR create new.
    # Actually, the requirement says "script generates a new file for each run", but we want to resume.
    # Let's find the MOST RECENT export file for this batch ID.
    
    exports_dir = "exports"
    if not os.path.exists(exports_dir):
        os.makedirs(exports_dir)
        
    pattern = os.path.join(exports_dir, f"invoices_batch{batch_id}_*.csv")
    existing_files = glob.glob(pattern)
    
    output_file = None
    processed_files = set()
    write_header = True

    # Check if there is a recent file (created today) we should append to
    if existing_files:
        # Sort by creation time
        latest_file = max(existing_files, key=os.path.getctime)
        print(f"Found existing export file: {latest_file}")
        
        # Read processed filenames
        try:
            with open(latest_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'filename' in row:
                        processed_files.add(row['filename'])
            write_header = False
            output_file = latest_file
            print(f"Resuming... {len(processed_files)} invoices already processed.")
        except Exception as e:
            print(f"Error reading existing CSV: {e}. Startihg fresh.")
    
    if not output_file:
        now = datetime.now()
        month_name = now.strftime("%b").lower()
        timestamp_str = now.strftime(f"%Y{month_name}%d_%H;%M")
        output_filename = f"invoices_batch{batch_id}_{timestamp_str}.csv"
        output_file = os.path.join(exports_dir, output_filename)
        print(f"Starting new export file: {output_file}")

    print(f"Running Batch {batch_id}")
    print(f"Input Directory: {input_dir}")
    print(f"Output File: {output_file}")

    if not os.path.exists(BASE_INPUT_DIR):
        os.makedirs(BASE_INPUT_DIR)
        print(f"Created base input directory: {BASE_INPUT_DIR}")

    if not os.path.exists(input_dir):
        print(f"Directory {input_dir} does not exist. Creating it now.")
        os.makedirs(input_dir)
        print(f"Please place your invoice images in {input_dir} and run the script again.")
        return

    all_images = glob.glob(os.path.join(input_dir, "*.jpg"))
    if not all_images:
        print(f"No invoice images found in {input_dir}.")
        return

    images_to_process = [img for img in all_images if os.path.basename(img) not in processed_files]

    if not images_to_process:
        print("All images have been processed.")
        return

    print(f"Processing {len(images_to_process)} new images with {MAX_WORKERS} threads...")

    # Initialize CSV header if needed
    if write_header:
        with open(output_file, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
            writer.writeheader()

    # Parallel Processing using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks
        futures = {executor.submit(process_single_image, img, output_file, FIELDNAMES): img for img in images_to_process}
        
        for future in tqdm(as_completed(futures), total=len(images_to_process), desc="Parallel Parsing"):
            # We don't really need the result here as it writes to CSV directly, 
            # but we iterate to update the progress bar as they complete.
            pass

    print(f"Processing complete. Data saved to {output_file}")
    print(f"Errors (if any) are logged to {LOG_FILE}")

if __name__ == "__main__":
    main()
