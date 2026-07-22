"""Shared helpers for isolated experiments built on the core dataset.

Every experiment is a self-contained, dated folder under scratch/experiments/.
This module gives each one the same contract:

- read the CORE dataset read-only,
- verify it is the exact version the experiment was pinned to (fingerprint),
- write outputs only into the experiment's own ``outputs/`` directory,
- record provenance (fingerprint, git commit, timestamps) in ``manifest.json``.

Import from an experiment's run.py like this::

    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
    from _lib import experiment as exp
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

# --------------------------------------------------------------------------- #
# Canonical locations
# --------------------------------------------------------------------------- #
# scratch/experiments/_lib/experiment.py -> repo root is parents[3]
REPO_ROOT = Path(__file__).resolve().parents[3]
SCRATCH = REPO_ROOT / "scratch"
SUMMARIES = SCRATCH / "summaries"
EXPERIMENTS = SCRATCH / "experiments"

# The core dataset every experiment reads (read-only).
CORE_FILES = {
    "roster": SUMMARIES / "core_players_roster.csv",
    "season_panel": SUMMARIES / "core_player_season_panel.csv",
    "gameweek_long": SUMMARIES / "core_player_gameweek_long.csv",
}

VALID_STATUS = {"planned", "running", "complete", "abandoned", "superseded"}


# --------------------------------------------------------------------------- #
# Fingerprinting (core-dataset version pinning)
# --------------------------------------------------------------------------- #
def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _row_count(path: Path) -> int:
    with open(path, "rb") as f:
        return max(0, sum(1 for _ in f) - 1)  # minus header


def core_fingerprint() -> dict:
    """Return {name: {sha256, rows, bytes}} for the current core dataset."""
    fp = {}
    for name, path in CORE_FILES.items():
        if not path.exists():
            raise FileNotFoundError(f"Core file missing: {path}")
        fp[name] = {
            "file": str(path.relative_to(REPO_ROOT)),
            "sha256": sha256_file(path),
            "rows": _row_count(path),
            "bytes": path.stat().st_size,
        }
    return fp


def verify_core(expected: dict) -> None:
    """Raise if the current core dataset differs from the pinned fingerprint."""
    current = core_fingerprint()
    drift = []
    for name, exp_meta in expected.items():
        cur = current.get(name)
        if cur is None:
            drift.append(f"{name}: missing from current core")
        elif cur["sha256"] != exp_meta.get("sha256"):
            drift.append(f"{name}: sha256 changed "
                         f"({exp_meta.get('sha256','?')[:12]} -> {cur['sha256'][:12]})")
    if drift:
        raise RuntimeError(
            "Core dataset has changed since this experiment was pinned:\n  "
            + "\n  ".join(drift)
            + "\nRe-pin deliberately (new experiment) rather than reusing this one.")


# --------------------------------------------------------------------------- #
# Loading the core (read-only intent)
# --------------------------------------------------------------------------- #
def load_core(verify: dict | None = None):
    """Load the three core layers as DataFrames. If ``verify`` (a pinned
    fingerprint) is given, assert the core is unchanged first."""
    import pandas as pd
    if verify is not None:
        verify_core(verify)
    return {name: pd.read_csv(path) for name, path in CORE_FILES.items()}


# --------------------------------------------------------------------------- #
# Manifests
# --------------------------------------------------------------------------- #
def load_manifest(exp_dir: Path) -> dict:
    return json.loads((Path(exp_dir) / "manifest.json").read_text(encoding="utf-8"))


def save_manifest(exp_dir: Path, manifest: dict) -> None:
    (Path(exp_dir) / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")


def git_commit_hash() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT,
            text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def exp_paths(run_file: str) -> dict:
    """Given an experiment's run.py __file__, return its standard paths and
    ensure outputs/ and validation/ exist."""
    exp_dir = Path(run_file).resolve().parent
    outputs = exp_dir / "outputs"
    validation = exp_dir / "validation"
    outputs.mkdir(exist_ok=True)
    validation.mkdir(exist_ok=True)
    return {"dir": exp_dir, "outputs": outputs, "validation": validation}
