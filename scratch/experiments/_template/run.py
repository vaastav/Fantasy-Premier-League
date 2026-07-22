"""Entry point for experiment __ID__ (__SLUG__).

Single command in, artifacts out. This script:
  1. verifies the core dataset matches the version pinned in manifest.json,
  2. loads the core (read-only),
  3. does the analysis,
  4. writes outputs to ./outputs/ and validation to ./validation/ only,
  5. updates manifest.json (outputs list, git commit) on success.

Run from the repository root:
    python scratch/experiments/__FOLDER__/run.py
"""

from __future__ import annotations

import sys
import pathlib

# Make the shared _lib importable regardless of CWD.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _lib import experiment as exp  # noqa: E402

SEED = 42


def main() -> None:
    paths = exp.exp_paths(__file__)
    manifest = exp.load_manifest(paths["dir"])

    # 1-2. Verify + load the pinned core dataset (read-only).
    pinned = manifest.get("core_dataset_fingerprint") or None
    core = exp.load_core(verify=pinned)
    roster = core["roster"]
    season = core["season_panel"]
    gw = core["gameweek_long"]

    # ------------------------------------------------------------------ #
    # 3. YOUR ANALYSIS HERE.
    #    Write derived artifacts into paths["outputs"].
    #    Save any validation checks into paths["validation"].
    # ------------------------------------------------------------------ #
    written = []
    # example:
    # out = paths["outputs"] / "result.csv"
    # some_summary_df.to_csv(out, index=False)
    # written.append(out.name)

    # 4-5. Record provenance on success.
    manifest["outputs"] = sorted(written)
    manifest["git_commit"] = exp.git_commit_hash()
    exp.save_manifest(paths["dir"], manifest)
    print(f"Experiment {manifest['id']} run complete. Outputs: {written}")


if __name__ == "__main__":
    main()
