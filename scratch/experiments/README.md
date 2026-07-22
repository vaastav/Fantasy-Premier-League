# Experiments

Every analysis is an **isolated, dated experiment**: in and out. Start it, run it
to completion, commit, push. The commit history and the auto-generated ledger
are two independent records of everything we've done.

## Foundation vs. experiments

- **Core dataset** (the shared foundation, read-only for everyone):
  - built by `build_core_dataset.py` → outputs in `../summaries/`
  - documented in `../summaries/CORE_DATASET_DICTIONARY.md`
  - **versioned**: every build is recorded in `../summaries/CORE_VERSIONS.json`
    as `core_vN`; a build with unchanged data is a no-op (idempotent).
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
2. **Pin the core version.** Each manifest records the core `core_vN` **and**
   its fingerprint (SHA-256 + row counts). `run.py` verifies the fingerprint
   before running and refuses if the core changed. If the core changed, that's
   a *new* experiment, not a silent rerun.
3. **Declare dependencies.** If an experiment builds on others, list their IDs
   in `depends_on` (validated at creation and by the ledger). This is what
   makes combining experiments later possible.
4. **Deterministic + captured env.** Set a seed; same inputs → same outputs.
   The manifest records the Python + pandas/numpy versions used.
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
`ledger.py`. Do not hand-edit it. It shows the live core version + fingerprint,
an index of all experiments, the dependency graph, a key-findings digest, and
any **dependency-integrity issues** (a broken or abandoned `depends_on`).
Run `python scratch/experiments/ledger.py --strict` to exit non-zero on issues
(useful as a pre-commit / CI guard).

## Core versions & resolving a stale pin

The core dataset will be rebuilt over time (new gameweeks, re-scrapes). Each
build is `core_vN` in `../summaries/CORE_VERSIONS.json`. Because every build is
committed, any past version is retrievable from git:

```bash
python scratch/experiments/resolve_core.py --list           # show all versions
python scratch/experiments/resolve_core.py core_v1          # locate it in git
python scratch/experiments/resolve_core.py core_v1 --extract /tmp/core_v1
```

If you try to run an experiment whose pinned core no longer matches the live
core, `run.py` fails with a message naming the pinned version and the exact
`resolve_core.py` command to retrieve it — so old experiments stay reproducible.
