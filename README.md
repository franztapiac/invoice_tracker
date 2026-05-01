# Image-to-Structured-Data Workflow for Construction Material Expense Tracking

## Executive Summary
The manual labour time required reduced from hours and days (not measure this time, but from experience) to the order of the amount of time it takes to take the pictures (<1 hour).

Tools used: Agentic coding, Google Antigravity, Python, Excel.

## Business problem
The construction company, to keep track of their expenses on a building project, manually recorded amounts from receipts into a spreadsheet. This work was time-consuming, error-prone and tedious.

### Methodology
1. Organise the invoices in data (optional, but facilitates validation).
2. Take pictures of the invoices. This manual process can be accelerated with a specific set up of paper stack placement.
3. Place receipt images in the `invoice_imgs` subdirectory.

The workflow works as follows:

Extracts data from invoice images based on the active test configuration.

- **Input**:
    - Configuration: `tests.txt` (Determines the active "Test XX").
    - Images: `invoice_imgs/test{ID}/` (e.g., `invoice_imgs/test02/`).
- **Output**: `exports/invoices_test{ID}_{timestamp}.csv`
- **Fields**: Date, Company, Invoice Number, Amount (USD priority), Currency, Filename.
- **Command**: `python execution/process_invoices.py`
- **Requirements**: `GOOGLE_API_KEY` in `.env`

## Results
In January 2026, this workflow processed 697 invoices. x/697 were completely correctly read. The rest (y/697) required manual corrections of extracted data. From experience, however, the time required to correct was less than the time required to complete the fields completely from zero.

## Recommendations
1. Execute this workflow for all invoices, but validate the results for receipts from Caribbean Concrete.
2. If the formatting on the receipt changes, validate the data extraction before relying on the workflow.

## Limitations
Gemini currently does not correctly register invoice numbers from Caribbean Concrete invoices.

## Next steps
1. Update workflow to also create ./invoice_imgs/ when the directory is initialised.
2. Update export format of workflow to better match format of master expenses database to better facilitate appending of new data.
3. Create an app that could be run by people without coding experience.