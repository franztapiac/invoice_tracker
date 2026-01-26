# Parse Invoices Directive

## Goal
Parse all invoice images in `invoice_imgs/` and extract structured data into a local CSV file `invoices.csv`.


## inputs
- `invoice_imgs/`: Directory containing `.jpg` invoice images.
- `.env`: Must contain `GOOGLE_API_KEY`.

## Execution
Run the python script:
```bash
python execution/process_invoices.py
```

## Outputs
- `invoices.csv`: CSV file with columns: `date`, `company`, `amount`, `currency`, `filename`.

## Edge Cases
- If `invoice_imgs/` is empty, exit gracefully.
- If API fails, log error and continue to next image.
