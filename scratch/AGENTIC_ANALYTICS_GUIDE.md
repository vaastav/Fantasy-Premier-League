# Agentic Analytics Guide

These rules guide agent-assisted coding and analysis in this repository. The project analyzes a large Fantasy Premier League dataset, so analytical work must protect raw data, preserve reproducibility, and keep each stage of the pipeline explicit.

## Core Principles

1. **Never overwrite raw data or data frames in place without state management.**
   - Treat files under canonical data locations, especially `data/`, as immutable inputs.
   - Write derived outputs to new files with descriptive names, timestamps, run IDs, or versioned directories.
   - If a data frame must be transformed, assign the result to a new variable that names the pipeline stage.

2. **Separate ingestion, cleaning, feature engineering, and visualization.**
   - Keep these steps in distinct files or distinct functions with narrow responsibilities.
   - Do not mix plotting code with raw ingestion or cleaning logic.
   - Prefer a pipeline flow like: ingest → validate → clean → validate → engineer features → validate → summarize → visualize.

3. **Write validation checkpoints before analytical functions run.**
   - Check file existence, schemas, expected columns, row counts, null rates, duplicate keys, ranges, and categorical domains.
   - Save validation outputs under `scratch/validation/` or an equivalent reviewed location.
   - Analytical functions should fail fast when required validation artifacts are missing or stale.

4. **Compute vectors and summaries before plotting.**
   - Build data vectors and aggregate summary tables first.
   - Save the summary tables under `scratch/summaries/` before visualization.
   - Pass only summarized data into plot functions; plot functions should not read raw datasets.

5. **Enforce hard environment boundaries and relative paths.**
   - Use repository-relative paths and avoid absolute local-machine paths.
   - Keep exploratory outputs inside `scratch/` unless a reviewer approves promotion.
   - Do not read from or write to locations outside the repository without an explicit documented reason.

## Expected Agent Workflow

Before coding an analysis, an agent should:

1. Identify the input files and document their relative paths.
2. Define expected schemas and quality checks.
3. Create or update a validation checkpoint.
4. Write analytical code that consumes validated inputs only.
5. Save derived summary tables before producing charts.
6. Generate visualizations from summary tables only.
7. Record commands, assumptions, and outputs in experiment notes.

## Promotion Criteria

Scratch work may be promoted into production modules only when:

- Raw inputs remain unchanged.
- Validation checkpoints exist and are reproducible.
- Pipeline stages are separated into clear functions or files.
- Outputs are written to intentional, documented paths.
- The work can be rerun from repository-relative paths.
