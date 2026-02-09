# Verify Invoices Directive

## Goal
Verify the accuracy of extracted invoice data by comparing the CSV records against the original invoice images using a generative AI model. This workflow assigns a confidence score and suggests corrections for potential errors (e.g., '8' vs 'B', currency mismatches).

## Inputs
- `selected_exports.txt`: A list of relative paths to CSV files to verify (e.g., `exports/invoices_test02_2026jan31_17;49.csv`).
- `invoice_imgs/`: Directory containing the source images (referenced by filenames in the CSV).
- `.env`: Must contain `GOOGLE_API_KEY`.

## Execution
Run the python script:
```bash
python execution/verify_invoices.py
```

## Outputs
- For each input CSV `path/to/file.csv`, a new file `path/to/file_verified.csv` is created.
- **New Columns**:
    - `confidence_score`: 0-100 score of data accuracy.
    - `verification_notes`: AI's explanation of the score.
    - `suggested_corrections`: JSON-formatted corrections if errors are found.

## Logic Rules
- **Verification Prompt**: The model is shown the image and the extracted data and asked to verify strict accuracy.
- **Focus Areas**: Explicitly checks for common OCR errors (8/B, 0/O/D) and currency consistency.
- **Numeric Formatting**: The QC process is instructed to ignore trivial differences in trailing zeros (e.g., `381.9` == `381.90`).
- **Concurrency**: Uses parallel processing to handle multiple invoices efficiently.
