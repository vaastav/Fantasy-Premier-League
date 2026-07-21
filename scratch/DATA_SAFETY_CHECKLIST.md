# Data Safety Checklist

Use this checklist before running or committing any analytics work.

## Path Boundaries

- [ ] All paths are relative to the repository root.
- [ ] Outputs are written under `scratch/` or another explicitly approved derived-output directory.
- [ ] No code writes outside the repository tree.
- [ ] No code mutates files under canonical raw-data locations.

## Raw Data Protection

- [ ] Raw files are opened read-only by convention.
- [ ] Derived files use new filenames or versioned output directories.
- [ ] Transformations create new data-frame variables instead of overwriting source variables in place.
- [ ] Any stateful step records its input path, output path, command, and timestamp or run ID.

## Pipeline Separation

- [ ] Ingestion logic is separate from cleaning logic.
- [ ] Cleaning logic is separate from feature engineering.
- [ ] Feature engineering is separate from summarization.
- [ ] Visualization functions accept summarized tables only.

## Validation Checkpoints

- [ ] Input files exist and are non-empty.
- [ ] Required columns are present.
- [ ] Key columns have expected uniqueness or documented duplicate behavior.
- [ ] Numeric ranges and categorical domains are checked.
- [ ] Null rates are measured and documented.
- [ ] Validation results are saved before downstream analysis runs.

## Visualization Safety

- [ ] Vectors or aggregates are computed before plotting.
- [ ] Summary tables are saved before plot generation.
- [ ] Plot functions do not read raw data directly.
- [ ] Chart outputs include references to the summary table that generated them.
