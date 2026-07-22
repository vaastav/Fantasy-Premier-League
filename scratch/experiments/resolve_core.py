"""Resolve and retrieve a historical core-dataset version.

Because every core build is committed, old versions are retrievable from git.
This tool maps a registry version (e.g. core_v1) to the commit that contains it
and can extract those exact files for re-running a stale-pinned experiment.

Usage (from repo root):
    python scratch/experiments/resolve_core.py --list
    python scratch/experiments/resolve_core.py core_v1
    python scratch/experiments/resolve_core.py core_v1 --extract /tmp/core_v1
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import experiment as exp  # noqa: E402


def _version_entry(version: str) -> dict:
    for v in exp.load_core_versions()["versions"]:
        if v["version"] == version:
            return v
    raise SystemExit(f"Unknown version '{version}'. Try --list.")


def cmd_list() -> None:
    reg = exp.load_core_versions()["versions"]
    live = exp.current_core_version()
    if not reg:
        print("No core versions registered yet. Run build_core_dataset.py.")
        return
    print(f"{'version':10} {'built':12} {'rows (panel)':14} live?")
    for v in reg:
        rows = v["row_counts"].get("season_panel", "?")
        mark = "  <== LIVE" if v["version"] == live else ""
        print(f"{v['version']:10} {v.get('date_built','?'):12} {str(rows):14}{mark}")


def cmd_resolve(version: str, extract: str | None) -> None:
    entry = _version_entry(version)
    if version == exp.current_core_version():
        print(f"{version} is the LIVE core on disk (scratch/summaries/).")
        if not extract:
            return
    commit = exp.find_commit_for_fingerprint(entry["fingerprint"])
    if not commit:
        raise SystemExit(
            f"Could not locate {version} in git history. It may be uncommitted "
            "or in history not present in this clone.")
    print(f"{version} lives in commit {commit}")
    for name, path in exp.CORE_FILES.items():
        rel = str(path.relative_to(exp.REPO_ROOT))
        print(f"  git show {commit}:{rel}")

    if extract:
        dest = Path(extract)
        dest.mkdir(parents=True, exist_ok=True)
        for name, path in exp.CORE_FILES.items():
            rel = str(path.relative_to(exp.REPO_ROOT))
            blob = subprocess.check_output(
                ["git", "show", f"{commit}:{rel}"], cwd=exp.REPO_ROOT)
            (dest / path.name).write_bytes(blob)
        print(f"Extracted {version} ({len(exp.CORE_FILES)} files) -> {dest}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("version", nargs="?", help="e.g. core_v1")
    ap.add_argument("--list", action="store_true", help="list registered versions")
    ap.add_argument("--extract", metavar="DIR", help="extract the version's files to DIR")
    args = ap.parse_args()

    if args.list or not args.version:
        cmd_list()
        return
    cmd_resolve(args.version, args.extract)


if __name__ == "__main__":
    main()
