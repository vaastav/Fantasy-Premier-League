# Experiments

Every analysis is an **isolated, dated experiment**: in and out. Start it, run it
to completion, commit, push. The commit history and the auto-generated ledger
are two independent records of everything we've done.

## Foundation vs. experiments

- **Core dataset** (the shared foundation, read-only for everyone):
  - built by `build_core_dataset.py` → outputs in `../summaries/`
  - documented in `../summaries/CORE_DATASET_DICTIONARY.md`
  - log: `EXPERIMENT_LOG_core_dataset.md`
- **Experiments** (this folder): one subfolder per experiment, named
  `NNN__YYYY-MM-DD__slug/`. Each is self-contained.

## Anatomy of an experiment

```
NNN__YYYY-MM-DD__slug/
├── manifest.json     # machine-readable metadata (feeds the ledger)
├── README.md         # question, rationale, method, results, conclusion
├── run.py            # single entrypoint: core in (read-only) → outputs/ out
├── outputs/          # derived artifacts owned by this experiment
└── validation/       # this experiment's own checks
```

## Rules that keep it tractable

1. **Read the core, never write it.** Experiments read `../summaries/core_*.csv`
   read-only and write only inside their own `outputs/` and `validation/`.
   Never edit `data/` or the shared summaries.
2. **Pin the core version.** `run.py` verifies the core-dataset fingerprint in
   `manifest.json` before running. If the core changed, that's a *new*
   experiment, not a silent rerun.
3. **Declare dependencies.** If an experiment builds on others, list their IDs
   in `depends_on`. This is what makes combining experiments later possible.
4. **Deterministic.** Set a seed; same inputs → same outputs.
5. **Status is honest.** `planned → running → complete`, or `abandoned` /
   `superseded` with a reason. Dead ends stay documented — never deleted.
6. **One experiment, one commit (at completion).** Commit prefix `exp(NNN): …`
   so `git log --grep 'exp('` reads as a ledger. Then push.

## Workflow

```bash
# 1. scaffold (auto-assigns next ID, pins the current core fingerprint)
python scratch/experiments/new_experiment.py my-idea \
    --title "My idea" --author me --rationale "why" [--depends-on 001 004]

# 2. write the README (question/rationale/method) and implement run.py

# 3. run it (in and out)
python scratch/experiments/<folder>/run.py

# 4. finalize: set status=complete + key_findings in manifest.json, then
python scratch/experiments/ledger.py        # regenerate the ledger

# 5. commit + push (the commit history is itself a ledger)
git add scratch/experiments/<folder> scratch/experiments/EXPERIMENTS_LEDGER.md
git commit -m "exp(NNN): <one-line summary>"
git push
```

## The ledger

`EXPERIMENTS_LEDGER.md` is **auto-generated** from every `manifest.json` by
`ledger.py`. Do not hand-edit it. It shows the core-dataset fingerprint, an
index of all experiments, the dependency graph, and a digest of key findings —
the map for building new analyses on top of prior ones.
