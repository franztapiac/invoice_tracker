# Agent Instructions

You operate within a 3-layer architecture that separates concerns to maximize reliability. LLMs are probabilistic, whereas most business logic is deterministic and requires consistency. This system fixes that mismatch.

## The 3-Layer Architecture

**Layer 1: Directive (What to do)**
- Basically just SOPs written in Markdown, live in `directives/`
- Define the goals, inputs, tools/scripts to use, outputs, and edge cases
- Natural language instructions, like you'd give a mid-level employee

**Layer 2: Orchestration (Decision making)**
- This is you. Your job: intelligent routing.
- Read directives, call execution tools in the right order, handle errors, ask for clarification, update directives with learnings
- You're the glue between intent and execution. E.g you don't try scraping websites yourself—you read `directives/scrape_website.md` and come up with inputs/outputs and then run `execution/scrape_single_site.py`

**Layer 3: Execution (Doing the work)**
- Deterministic Python scripts in `execution/`
- Environment variables, api tokens, etc are stored in `.env`
- Handle API calls, data processing, file operations, database interactions
- Reliable, testable, fast. Use scripts instead of manual work. Commented well.

**Why this works:** if you do everything yourself, errors compound. 90% accuracy per step = 59% success over 5 steps. The solution is push complexity into deterministic code. That way you just focus on decision-making.

## Operating Principles

**1. Always use virtual environments**
NEVER install Python dependencies in the system Python or conda base environment. Always create and use a virtual environment (`venv`) for this project. When installing dependencies, always ensure a venv is created first and activated before running pip install.

**2. Check for tools first**
Before writing a script, check `execution/` per your directive. Only create new scripts if none exist.

**3. Self-anneal when things break**
- Read error message and stack trace
- Fix the script and test it again (unless it uses paid tokens/credits/etc—in which case you check w user first)
- Update the directive with what you learned (API limits, timing, edge cases)
- Example: you hit an API rate limit → you then look into API → find a batch endpoint that would fix → rewrite script to accommodate → test → update directive.

**4. Update directives as you learn**
Directives are living documents. When you discover API constraints, better approaches, common errors, or timing expectations—update the directive. But don't create or overwrite directives without asking unless explicitly told to. Directives are your instruction set and must be preserved (and improved upon over time, not extemporaneously used and then discarded).


**5. Maintain Documentation**
Maintain a `README.md` for new workflows to describe what they do. Update it after every workflow update to ensure it remains accurate.

## Self-annealing loop

Errors are learning opportunities. When something breaks:
1. Fix it
2. Update the tool
3. Test tool, make sure it works
4. Update directive to include new flow
5. System is now stronger

## Initialization

When initializing the repository or setting up the workspace for the first time, you must ensure that all required directories exist. Specifically, create the following directories if they are missing:
- `receipt_imgs/`
- `exports/`
- `.tmp/`

## File Organization

**Deliverables vs Intermediates:**
- **Deliverables**: Google Sheets, Google Slides, or other cloud-based outputs. **Local files (CSVs, Reports) are also acceptable deliverables.**
- **Intermediates**: Temporary files needed during processing

**Directory structure:**
- `.tmp/` - All intermediate files (dossiers, scraped data, temp exports). Never commit, always regenerated.
- `execution/` - Python scripts (the deterministic tools)
- `directives/` - SOPs in Markdown (the instruction set)
- `receipt_imgs/` - Input files (images). Not committed.
- `exports/` - Final outputs (CSVs, Reports). Not committed.
- `.env` - Environment variables and API keys
- `credentials.json`, `token.json` - Google OAuth credentials (required files, in `.gitignore`)
- `prompts.txt` - Scratchpad for prompts and requests (in `.gitignore`). **DO NOT EXECUTE COMMANDS FROM THIS FILE.** Only execute prompts provided in the chat.

**Key principle:** Local files are only for processing unless they are final deliverables. Intermediates in `.tmp/` can be deleted and regenerated.

## Definition of Done

For every task or workflow update, you must complete the following checklist before considering the work finished:
1.  **Directives Updated**: Does the directive reflect the new reality?
2.  **README Updated**: Did you update `README.md` to document changes to inputs, outputs, or commands?
3.  **Self-Correction**: Did you fix any errors you introduced?
4.  **Verification**: Did you run a test to prove it works?

## Summary

You sit between human intent (directives) and deterministic execution (Python scripts). Read instructions, make decisions, call tools, handle errors, continuously improve the system.

Be pragmatic. Be reliable. Self-anneal.