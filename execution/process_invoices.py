import os
import csv
import json
import glob
import time
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
INPUT_DIR = "invoice_imgs"
OUTPUT_FILE = "invoices.csv"
FIELDNAMES = ['date', 'company', 'amount', 'currency', 'filename']

def extract_invoice_data(image_path):
    """
    Uploads an image to Gemini and extracts invoice details.
    """
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        
        with open(image_path, "rb") as f:
            image_data = f.read()
            
        prompt = """
        Analyze this invoice image and extract the following details in JSON format:
        - date (YYYY-MM-DD)
        - company (string)
        - amount (number)
        - currency (string, e.g., USD, EUR)
        
        Return ONLY the JSON object.
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
    if not os.path.exists(INPUT_DIR):
        print(f"Directory {INPUT_DIR} does not exist.")
        return

    all_images = glob.glob(os.path.join(INPUT_DIR, "*.jpg"))
    if not all_images:
        print("No invoice images found.")
        return

    processed_files = set()
    write_header = True

    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'filename' in row:
                        processed_files.add(row['filename'])
            write_header = False
            print(f"Found {len(processed_files)} already processed invoices.")
        except Exception as e:
            print(f"Error reading existing CSV: {e}")

    images_to_process = [img for img in all_images if os.path.basename(img) not in processed_files]

    if not images_to_process:
        print("All images have been processed.")
        return

    print(f"Processing {len(images_to_process)} new images...")

    # Open file in append mode
    with open(OUTPUT_FILE, 'a', newline='') as csvfile:
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

    print(f"Processing complete. Data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
