"""Build the ALL-PLAYERS season-aggregate panel (superset of the 389 core).

The core dataset is intersected to the 389 players present in all three seasons.
Some analyses (e.g. team-composition by archetype) need EVERY player in a season,
not just the ever-presents. This builder produces the same season-aggregate panel
schema as the core, but for all players each season (managers excluded), WITHOUT
the cross-season intersection.

It reuses the core builder's ingestion + panel logic so the two panels are
schema-identical and the 389 core is an exact subset of this table.

Output (scratch only, data/ untouched):
- scratch/summaries/all_players_season_panel.csv

Run from the repository root:
    python scratch/experiments/build_all_players_panel.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_core_dataset as core  # noqa: E402

OUT = core.SUMMARIES_DIR / "all_players_season_panel.csv"


def main() -> None:
    core.SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)

    raw_by_season = {s: core.read_players_raw(s) for s in core.SEASONS}
    teams_by_season = {s: core.read_teams(s) for s in core.SEASONS}

    # All players (managers/element_type 5 excluded), NOT intersected.
    frames = []
    for s in core.SEASONS:
        df = raw_by_season[s]
        frames.append(df[~df["element_type"].isin(core.NON_PLAYER_TYPES)].copy())
    all_raw = pd.concat(frames, ignore_index=True)

    panel = core.build_season_panel(all_raw, teams_by_season)
    panel.to_csv(OUT, index=False, encoding="utf-8")

    # -- validation ------------------------------------------------------- #
    checks = {}
    checks["rows"] = int(len(panel))
    checks["per_season"] = {s: int((panel["season"] == s).sum()) for s in core.SEASONS}
    checks["unique_code_season"] = bool(not panel.duplicated(["code", "season"]).any())
    checks["positions_ok"] = sorted(set(panel["position"].dropna())) == ["DEF", "FWD", "GK", "MID"]

    # The 389 core must be an exact subset of this panel.
    core_panel = pd.read_csv(core.SUMMARIES_DIR / "core_player_season_panel.csv")
    core_keys = set(map(tuple, core_panel[["code", "season"]].values))
    all_keys = set(map(tuple, panel[["code", "season"]].values))
    checks["core_is_subset"] = core_keys.issubset(all_keys)
    checks["n_ge_900_min"] = {s: int(((panel["season"] == s) & (panel["minutes"] >= 900)).sum())
                              for s in core.SEASONS}

    (core.SUMMARIES_DIR / "all_players_season_panel_validation.json").write_text(
        json.dumps(checks, indent=2), encoding="utf-8")

    print(f"Wrote {OUT.relative_to(core.REPO_ROOT)}  ({checks['rows']} rows)")
    print(f"  per season: {checks['per_season']}")
    print(f"  >=900 min:  {checks['n_ge_900_min']}")
    print(f"  core-389 is exact subset: {checks['core_is_subset']}")
    print(f"  unique (code,season): {checks['unique_code_season']} | positions ok: {checks['positions_ok']}")


if __name__ == "__main__":
    main()
