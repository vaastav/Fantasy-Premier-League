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
import sys
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

# Registry of every core-dataset version we have ever built.
CORE_VERSIONS_PATH = SUMMARIES / "CORE_VERSIONS.json"

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
        pinned_version = None
        for v in load_core_versions()["versions"]:
            if _fingerprints_match(v["fingerprint"], expected):
                pinned_version = v["version"]
                break
        hint = (f"\nThis experiment was pinned to {pinned_version}. "
                f"Retrieve it with:\n  python scratch/experiments/resolve_core.py "
                f"{pinned_version} --extract <dir>" if pinned_version else
                "\nThe pinned core is not in the version registry (CORE_VERSIONS.json).")
        raise RuntimeError(
            "Core dataset has changed since this experiment was pinned:\n  "
            + "\n  ".join(drift) + hint
            + "\nRe-pin deliberately (new experiment) rather than reusing this one.")


# --------------------------------------------------------------------------- #
# Core-dataset versioning
# --------------------------------------------------------------------------- #
def load_core_versions() -> dict:
    if CORE_VERSIONS_PATH.exists():
        return json.loads(CORE_VERSIONS_PATH.read_text(encoding="utf-8"))
    return {"versions": []}


def _fingerprints_match(a: dict, b: dict) -> bool:
    """Compare two fingerprints by per-layer sha256 only."""
    if set(a) != set(b):
        return False
    return all(a[k].get("sha256") == b[k].get("sha256") for k in a)


def current_core_version() -> str | None:
    """Return the registry version whose fingerprint matches the core on disk,
    or None if the current core is unregistered (registry stale)."""
    try:
        current = core_fingerprint()
    except FileNotFoundError:
        return None
    for v in load_core_versions()["versions"]:
        if _fingerprints_match(v["fingerprint"], current):
            return v["version"]
    return None


def register_core_version(notes: str = "") -> tuple[str, bool]:
    """Ensure the core on disk is recorded in the registry. Idempotent: if the
    current fingerprint already matches the latest version, nothing is added.
    Returns (version, is_new)."""
    reg = load_core_versions()
    current = core_fingerprint()
    if reg["versions"] and _fingerprints_match(reg["versions"][-1]["fingerprint"], current):
        return reg["versions"][-1]["version"], False
    # Also allow matching an older version (e.g. a rebuild reverting a change).
    for v in reg["versions"]:
        if _fingerprints_match(v["fingerprint"], current):
            return v["version"], False

    n = len(reg["versions"]) + 1
    version = f"core_v{n}"
    reg["versions"].append({
        "version": version,
        "date_built": _today(),
        "git_commit_at_build": git_commit_hash(),
        "row_counts": {k: current[k]["rows"] for k in current},
        "fingerprint": current,
        "notes": notes,
    })
    CORE_VERSIONS_PATH.write_text(json.dumps(reg, indent=2), encoding="utf-8")
    return version, True


def find_commit_for_fingerprint(fingerprint: dict, layer: str = "season_panel") -> str | None:
    """Search git history for the commit whose version of a core file matches
    the pinned sha256. Lets a stale pin be resolved back to retrievable files."""
    rel = str(CORE_FILES[layer].relative_to(REPO_ROOT))
    want = fingerprint[layer]["sha256"]
    try:
        commits = subprocess.check_output(
            ["git", "log", "--format=%H", "--", rel],
            cwd=REPO_ROOT, text=True, stderr=subprocess.DEVNULL).split()
    except Exception:
        return None
    for c in commits:
        try:
            blob = subprocess.check_output(
                ["git", "show", f"{c}:{rel}"], cwd=REPO_ROOT, stderr=subprocess.DEVNULL)
        except Exception:
            continue
        if hashlib.sha256(blob).hexdigest() == want:
            return c
    return None


# --------------------------------------------------------------------------- #
# Environment capture
# --------------------------------------------------------------------------- #
def _today() -> str:
    import datetime as _dt
    return _dt.date.today().isoformat()


def capture_environment() -> dict:
    """Record the interpreter + key package versions so a rerun is comparable."""
    env = {"python": sys.version.split()[0], "packages": {}}
    for pkg in ("pandas", "numpy"):
        try:
            mod = __import__(pkg)
            env["packages"][pkg] = getattr(mod, "__version__", "unknown")
        except Exception:
            env["packages"][pkg] = "not-installed"
    return env


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


def experiment_dir_by_id(exp_id: str) -> Path:
    """Locate an experiment folder by its NNN id (e.g. '002')."""
    matches = sorted(EXPERIMENTS.glob(f"{exp_id}__*"))
    if not matches:
        raise FileNotFoundError(f"No experiment folder for id {exp_id}")
    return matches[0]


def load_experiment_output(exp_id: str, filename: str):
    """Load a CSV output from an upstream experiment as a DataFrame."""
    import pandas as pd
    return pd.read_csv(experiment_dir_by_id(exp_id) / "outputs" / filename)


def exp_paths(run_file: str) -> dict:
    """Given an experiment's run.py __file__, return its standard paths and
    ensure outputs/ and validation/ exist."""
    exp_dir = Path(run_file).resolve().parent
    outputs = exp_dir / "outputs"
    validation = exp_dir / "validation"
    outputs.mkdir(exist_ok=True)
    validation.mkdir(exist_ok=True)
    return {"dir": exp_dir, "outputs": outputs, "validation": validation}
