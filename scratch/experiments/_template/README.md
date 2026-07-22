# Experiment __ID__ — __SLUG__

> **Status:** planned · **Created:** __DATE__ · **Author:**
>
> One-line rationale: _why this experiment exists._

## Question

_What precise question does this experiment answer? State it so success/failure
is unambiguous._

## Rationale

_Why now, why this approach, what prior experiment or observation motivated it.
Link upstream experiments by id if this builds on them._

## Method

_Inputs (core dataset version is pinned in `manifest.json`), transformations,
models, parameters, seed. Keep ingestion → validation → analysis → output
separated (see ../../AGENTIC_ANALYTICS_GUIDE.md)._

## How to run

```bash
python scratch/experiments/__FOLDER__/run.py
# outputs -> ./outputs/   validation -> ./validation/
```

## Results

_Tables, numbers, figures. Reference the output files that produced them._

## Interpretation

_What the results mean. Caveats and threats to validity._

## Conclusion

_Answer to the Question. Decision: keep / abandon / supersede. What (if
anything) should be promoted or built on next._

## Provenance

- Core dataset fingerprint: see `manifest.json`
- Git commit at completion: see `manifest.json`
