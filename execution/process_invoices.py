import os
import csv
import json
import glob
from dotenv import load_dotenv
import google.generativeai as genai

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

import time

# ...

def extract_invoice_data(image_path):
    """
    Uploads an image to Gemini and extracts invoice details.
    """
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        
        # Add delay to respect rate limits
        time.sleep(2)
        
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
        print(f"Error processing {image_path}: {e}")
        return None

def main():
    if not os.path.exists(INPUT_DIR):
        print(f"Directory {INPUT_DIR} does not exist.")
        return

    images = glob.glob(os.path.join(INPUT_DIR, "*.jpg"))
    if not images:
        print("No invoice images found.")
        return

    print(f"Found {len(images)} images. Processing with Gemini...")
    
    results = []
    for img_path in images:
        print(f"Processing {img_path}...")
        data = extract_invoice_data(img_path)
        if data:
            data['filename'] = os.path.basename(img_path)
            results.append(data)

    if results:
        fieldnames = ['date', 'company', 'amount', 'currency', 'filename']
        with open(OUTPUT_FILE, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in results:
                writer.writerow(row)
        print(f"Successfully saved data to {OUTPUT_FILE}")
    else:
        print("No data extracted.")

if __name__ == "__main__":
    main()
