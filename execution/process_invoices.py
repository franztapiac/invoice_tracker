import os
import csv
import json
import glob
import time
import re
from datetime import datetime
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
TESTS_FILE = "tests.txt"
BASE_INPUT_DIR = "invoice_imgs"
FIELDNAMES = ['date', 'company', 'invoice_number', 'amount', 'currency', 'filename']

def get_latest_test_id():
    """
    Parses tests.txt to find the latest Test ID.
    Returns the test ID string (e.g., "02") or None if not found.
    """
    if not os.path.exists(TESTS_FILE):
        print(f"Error: {TESTS_FILE} not found.")
        return None

    try:
        with open(TESTS_FILE, 'r') as f:
            content = f.read()
        
        # Regex to find all "Test XX" headers
        matches = re.findall(r'Test\s+(\d+)', content)
        
        if matches:
            # Return the last one found
            return matches[-1]
        else:
            return None
    except Exception as e:
        print(f"Error reading {TESTS_FILE}: {e}")
        return None

def extract_invoice_data(image_path):
    """
    Uploads an image to Gemini and extracts invoice details.
    """
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        
        with open(image_path, "rb") as f:
            image_data = f.read()
            
        prompt = """
        Analyze this invoice image and extract the following details in JSON format.
        
        Extraction Rules:
        1. **Company**: Extract the common trading name of the company. 
           - Remove legal suffixes like 'Inc', 'N.V.', 'B.V.', 'Ltd', 'S.A.', etc. (e.g., 'Island Water World Inc N.V' -> 'Island Water World').
           - If the logo/name is covered (e.g. by a receipt), look elsewhere in the document (headers, footers) for the company name.
        2. **Invoice Number**: Extract the invoice number (sometimes called 'slip #', 'bill #', etc.).
        3. **Date**: Extract the date in YYYY-MM-DD format.
        4. **Total Amount & Currency**:
           - Look for the TOTAL amount.
           - **CRITICAL**: If the amount is available in USD and another currency (e.g., NAF, ANG), YOU MUST extraction the USD amount and set currency to 'USD'.
           - Only use a different currency if USD is strictly NOT present or calculable.
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
            
        return json.loads(text)
    except Exception as e:
        # Log error to a file potentially, or just print
        return None

def main():
    test_id = get_latest_test_id()
    if not test_id:
        print("Could not determine Test ID from tests.txt.")
        return

    input_dir = os.path.join(BASE_INPUT_DIR, f"test{test_id}")
    
    # Generate output filename: exports/invoices_test02_2026jan31_14;02.csv
    now = datetime.now()
    month_name = now.strftime("%b").lower()
    timestamp_str = now.strftime(f"%Y{month_name}%d_%H;%M")
    output_filename = f"invoices_test{test_id}_{timestamp_str}.csv"
    output_file = os.path.join("exports", output_filename)

    print(f"Running Test {test_id}")
    print(f"Input Directory: {input_dir}")
    print(f"Output File: {output_file}")

    # Ensure exports directory exists, though user said it does
    if not os.path.exists("exports"):
        os.makedirs("exports")

    if not os.path.exists(input_dir):
        print(f"Directory {input_dir} does not exist.")
        return

    all_images = glob.glob(os.path.join(input_dir, "*.jpg"))
    if not all_images:
        print(f"No invoice images found in {input_dir}.")
        return

    processed_files = set()
    write_header = True

    # Note: For this new requirement, we are generating a NEW file every time, 
    # so we might NOT want to read processed files from the *new* file (since it doesn't exist yet).
    # But if we want to support resuming a run for the SAME csv name, we would check existence.
    # The requirement says "generate a new CSV file... named differently, according to date and time".
    # This implies a fresh start for each run unless the minute hasn't changed.
    
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'filename' in row:
                        processed_files.add(row['filename'])
            write_header = False
            print(f"Found {len(processed_files)} already processed invoices in {output_file}.")
        except Exception as e:
            print(f"Error reading existing CSV: {e}")

    images_to_process = [img for img in all_images if os.path.basename(img) not in processed_files]

    if not images_to_process:
        print("All images have been processed.")
        return

    print(f"Processing {len(images_to_process)} new images...")

    # Open file in append mode
    with open(output_file, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        
        if write_header:
            writer.writeheader()

        # Use tqdm for progress bar
        for img_path in tqdm(images_to_process, desc="Parsing Invoices"):
            data = extract_invoice_data(img_path)
            
            if data:
                data['filename'] = os.path.basename(img_path)
                writer.writerow(data)
                csvfile.flush() # Ensure it's written immediately
            
            # Rate limiting
            time.sleep(5)

    print(f"Processing complete. Data saved to {output_file}")

if __name__ == "__main__":
    main()
