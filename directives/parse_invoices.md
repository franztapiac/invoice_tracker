# Parse Invoices Directive

## Goal
Parse invoice images from the latest test directory (defined in `tests.txt`) and extract structured data into a timestamped local CSV file (e.g., `invoices_test02_2026jan31_14;02.csv`).

## Inputs
- `tests.txt`: Contains "Test XX" blocks to determine the active test ID.
- `invoice_imgs/test{ID}/`: Directory containing `.jpg` invoice images for the active test.
- `.env`: Must contain `GOOGLE_API_KEY`.

## Execution
Run the python script:
```bash
python execution/process_invoices.py
```

## Outputs
- `exports/invoices_test{ID}_{timestamp}.csv`: CSV file with columns: `date`, `company`, `invoice_number`, `amount`, `currency`, `filename`.
- `processing_errors.log`: Logs failed extractions with error details.

## Logic Rules
- **Invoice Number**: Extracted if available.
- **Currency**: USD is prioritized. If amounts appear in multiple currencies, USD is extracted.
- **Company Name**: Common trading name only. Legal suffixes (e.g., "N.V.") are removed.

## Edge Cases
- If `tests.txt` is missing or has no "Test XX" block, the script exits.
- If the specific test directory (e.g., `invoice_imgs/test02/`) is empty, exit gracefully.
- The script generates a new file for each run (based on minute-resolution timestamp).
- **Retries**: API calls are retried up to 3 times with exponential backoff. Failed images are logged to `processing_errors.log`.
