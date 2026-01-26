# Invoice Tracker

## Overview
This project contains workflows to process and track invoices.

## Workflows

### Parse Invoices
Extracts data from invoice images and saves to a local CSV.

- **Input**: Images in `invoice_imgs/`
- **Output**: `invoices.csv` (Local file)
- **Command**: `python execution/process_invoices.py`
- **Requirements**: `GOOGLE_API_KEY` in `.env`
