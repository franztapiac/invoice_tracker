# Image-to-Structured-Data Workflow for Construction Material Expense Tracking

## Executive Summary

Manual recording of receipt data into a database is time-consuming and error-prone. Given the recent advances in Artificial Intelligence (AI), I developed an AI-based workflow to automate and speed up this process. I built this workflow by prompting Gemini 3.1 Pro (High) through the Google Antigravity coding agent. As a result, the time required to record the data from 700 receipts into the master database was reduced from an estimated two to three days to an estimated 5-7 hours of receipt imaging, workflow execution, and data cleaning. Also, the workflow correctly extracted the data from 96% (664/689) of the receipts.


## Business problem
A private construction client in Sint Maarten employs people to manually record receipt information into an Excel spreadsheet. However, manual recording is time-consuming and is prone to errors. Given the recent advances in AI, could an AI-based workflow automate and speed up this process? The information includes date of purchase, merchant name, receipt number, and purchase amount.


### Methodology:
1. Initiliased the directory structured according to `directives.md`  by prompting a Large Language Model (LLM) through Google Antigravity.
2. Developed prompts to guide Gemini 3.1 Pro (High) to build the workflow.
3. Organised receipts by date (optional, but facilitates validation).
4. Took pictures of the receipts with a smartphone. This manual process can be streamlined by having a system for picture taking. For example, the system used here simply had remaining receipts on the left, the current receipt at the centre, and the photographed receipts on the right.
5. Placed the receipt images in the `receipt_imgs` directory, within a subdirectory for the batch (e.g., `receipt_imgs/batch01/`).
6. Updated `batches.txt` to include the batch information (number of receipts being processed and execution date).
7. Provided a Gemini API key through `GOOGLE_API_KEY` in `.env`.
8. Prompted an LLM through the Google Antigravity to execute the workflow. Before this, the LLM was asked to familiarise itself with the directory, starting with directives.md.
9. Validated the output in `exports/invoices_batch{ID}_{timestamp}.csv`. For data that was not extracted correctly, the original receipts were checked and the data was corrected manually. This step was streamlined by first asking the LLM to do compare each row of data with its corresponding image and generate data cleaning suggestions.


## Skills

- Prompt engineering
- Google Antigravity
- Python
- Excel


## Results & Limitations
In February 2026, this workflow extracted data from 689 invoices. The workflow correctly extracted data from 664/689 invoices. The rest (25/689) required manual corrections. From experience of having to manually record the receipt data, the time required to manually record the data from 700 receipts was greater than the cumulative time required to image the receipts, execute the workflow, and correct unclean data. It was estimated that it would previously take two to three days to fully record the data from 700 receipts manually. Using the workflow, the time required to record the data to the master database was reduced to an estimate of 5-7 hours.

The workflow did not perfectly extract data from receipts of the following companies: Caribbean Concrete, Earth Building Supplies and Rental Services, Sint Maarten Building Supply / SBS Cole Bay. The errors likely arose from how the receipts were printed. The printed receipt details were sometimes not printed within the dedicated formatting boxes, but instead on the box borders. This intersection likely rendered the receipt text illegible to the LLM. In other cases, the ink on old receipts was vanishing.


## Recommendations

The workflow strengths are that it works very well on receipts that are clearly legible. If receipts begin to be challenging for a human to read, they will be challenging for the AI to read. Therefore:

- Execute this workflow for all invoices, and validate the results for receipts that are somewhat illegible, including those from Caribbean Concrete, Earth Building Supplies and Rental Services, and Sint Maarten Building Supply / SBS Cole Bay.


## Next Steps:
1. Update the export format of the workflow to better match the format of the master expenses database. Doing so will facilitate the appending of new data.
2. Create an app that could be executed by individuals without (agentic) coding experience.