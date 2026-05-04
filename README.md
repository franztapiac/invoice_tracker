# Image-to-Structured-Data Workflow for Construction Material Expense Tracking

## Executive Summary
The manual labour time required reduced from hours and days (not measure this time, but from experience) to the order of the amount of time it takes to take the pictures (<1 hour).

## Business problem
A private construction client in Sint Maarten employs people to manually record receipt information into an Excel spreadsheet. However, manual recording is time-consuming and is prone to errors. Given the recent advances in AI, could an AI-based workflow automate and speed up this process? The information includes date of purchase, merchant name, receipt number, and purchase amount.

### Methodology:
1. Organised receipts by date (optional, but facilitates validation).
2. Took pictures of the receipts with a smartphone. This manual process can be streamlined by having a system for picture taking. For example, the system used here simply had remaining receipts on the left, the current receipt at the centre, and the photographed receipts on the right.
3. Placed the receipt images in the `receipt_imgs` directory, within a subdirectory for the batch (e.g., `receipt_imgs/batch01/`).
4. Updated `batches.txt` to include the batch information (number of receipts being processed and execution date).
5. Prompted an LLM through the Google Antigravity chat box to execute the workflow. Before this, the LLM was asked to familiarise itself with the directory, starting with directives.md.
6. Validated the output in `exports/invoices_batch{ID}_{timestamp}.csv`. For data that was not extracted correctly, the original receipts were checked and the data was corrected manually. This step was streamlined by first asking the LLM to do compare each row of data with its corresponding image and generate data cleaning suggestions.

The workflow works as follows:

Extracts data from invoice images based on the active batch configuration.

- **Input**:
    - Configuration: `batches.txt` (Determines the active "Batch XX").
    - Images: `receipt_imgs/batch{ID}/` (e.g., `receipt_imgs/batch02/`).
- **Output**: `exports/invoices_batch{ID}_{timestamp}.csv`
- **Fields**: Date, Company, Invoice Number, Amount (USD priority), Currency, Filename.
- **Command**: `python execution/process_invoices.py`
- **Requirements**: `GOOGLE_API_KEY` in `.env`


## Skills
Tools used: Agentic coding, Google Antigravity, Python, Excel.


## Results, Limitations & Business Recommendations
In January 2026, this workflow processed 697 invoices. x/697 were completely correctly read. The rest (y/697) required manual corrections of extracted data. From experience, however, the time required to correct was less than the time required to complete the fields completely from zero.

Gemini currently does not correctly register invoice numbers from Caribbean Concrete invoices. The printed receipt details may not be printed within the dedicated boxes, but intersect with the box borders. Therefore, the intersections render the receipt text illegible to the AI. Otherwise, old receipts whose ink is vanishing also do not support AI reading.

1. Execute this workflow for all invoices, but validate the results for receipts from Caribbean Concrete.
2. If the formatting on the receipt changes, validate the data extraction before relying on the workflow.

## Next Steps:
1. Update export format of workflow to better match format of master expenses database to better facilitate appending of new data.
2. Create an app that could be run by people without coding experience.

<!--
Workflow:

The workflow was built through subsequent prompts, first starting with a build prompt, asking the agent to initialise the directory according to the high levels directives in GEMINI.md. (call it directives.md).

Receipts were ordered chronologically, and images were taken with a smartphone. Then the images were stored in ./data. The workflow was then executed.

strengths: works on receipts that are clearly legible
If they begin to be challenging for a human to read, they will be challenging for the AI to read

companies receipt worked for: 
companies receipt struggled in: Caribbean Concrete.
-->