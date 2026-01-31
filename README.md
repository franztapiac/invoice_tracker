# Invoice Tracker

## Overview
This project contains workflows to process and track invoices.

## Workflows

### Parse Invoices
Extracts data from invoice images based on the active test configuration.

- **Input**:
    - Configuration: `tests.txt` (Determines the active "Test XX").
    - Images: `invoice_imgs/test{ID}/` (e.g., `invoice_imgs/test02/`).
- **Output**: `exports/invoices_test{ID}_{timestamp}.csv`
- **Fields**: Date, Company, Invoice Number, Amount (USD priority), Currency, Filename.
- **Command**: `python execution/process_invoices.py`
- **Requirements**: `GOOGLE_API_KEY` in `.env`
