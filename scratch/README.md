# Scratch Workspace

This folder is reserved for exploratory, agent-assisted analytics work that should remain isolated from the repository's source datasets and production scripts until it is reviewed and intentionally promoted.

## Purpose

Use `scratch/` for:

- Draft notebooks, scripts, and intermediate documentation for fantasy Premier League data analysis.
- Temporary summary tables derived from raw data.
- Validation reports that document assumptions before analysis or visualization.
- Experiment logs that explain what was run, which inputs were used, and which outputs were generated.

Do **not** use `scratch/` for:

- Mutable copies of raw datasets that can be mistaken for source data.
- In-place edits to files under `data/` or any other canonical data location.
- Production code unless it is later moved into the appropriate top-level module after review.

## Recommended Layout

```text
scratch/
├── README.md
├── AGENTIC_ANALYTICS_GUIDE.md
├── DATA_SAFETY_CHECKLIST.md
├── experiments/
├── validation/
├── summaries/
└── visuals/
```

- `experiments/`: exploratory scripts, notebooks, and notes.
- `validation/`: data-validation checkpoints and schema/quality reports.
- `summaries/`: saved aggregate tables used by downstream analysis or plots.
- `visuals/`: charts generated only from summarized data.

Keep paths relative to the repository root and document every generated artifact in the experiment notes that created it.
