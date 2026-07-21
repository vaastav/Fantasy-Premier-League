"""Build the core 3-season common-player dataset.

Goal
----
Produce a canonical working dataset covering the last three FPL seasons
(2023-24, 2024-25, 2025-26), restricted to the players who are present in
*all three* seasons. A player who left before, or joined after, the window is
excluded.

Identity key
------------
Players are matched across seasons on the stable FPL ``code`` (the permanent
per-person identifier). The per-season ``id`` / ``element`` numbers are reused
each season and therefore cannot be used to join across seasons.

Outputs (written under scratch/, never into data/)
--------------------------------------------------
- scratch/summaries/core_players_roster.csv        (one row per player)
- scratch/summaries/core_player_season_panel.csv   (one row per player-season)
- scratch/summaries/core_player_gameweek_long.csv  (one row per player-gameweek)
- scratch/validation/core_dataset_validation.json  (machine-readable checks)
- scratch/validation/core_dataset_validation.md    (human-readable report)
- scratch/summaries/core_dataset_manifest.json     (run manifest / provenance)

Design principles (see scratch/AGENTIC_ANALYTICS_GUIDE.md)
---------------------------------------------------------
- data/ is treated as read-only. Nothing here writes into it.
- Ingestion, validation, assembly, and serialization are separated.
- Validation checkpoints are written before the dataset is considered final.
- The season panel is sourced from the authoritative FPL season snapshot
  (players_raw.csv) and *cross-checked* against gameweek-level sums.

Run from the repository root:  python scratch/experiments/build_core_dataset.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------- #
# Repo-relative paths (this file lives at scratch/experiments/)
# --------------------------------------------------------------------------- #
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"                     # read-only source data
SUMMARIES_DIR = REPO_ROOT / "scratch" / "summaries"
VALIDATION_DIR = REPO_ROOT / "scratch" / "validation"

SEASONS = ["2023-24", "2024-25", "2025-26"]

# FPL element_type -> position. 5 = "manager" (Assistant Manager chip), not a player.
POSITION_MAP = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD", 5: "MNG"}
NON_PLAYER_TYPES = {5}

# Season-aggregate stat columns taken from players_raw.csv.
SEASON_STAT_COLS = [
    "total_points", "minutes", "starts",
    "goals_scored", "assists",
    "expected_goals", "expected_assists", "expected_goal_involvements",
    "clean_sheets", "goals_conceded", "expected_goals_conceded",
    "saves", "penalties_saved", "penalties_missed", "own_goals",
    "yellow_cards", "red_cards",
    "bonus", "bps",
    "influence", "creativity", "threat", "ict_index",
    "now_cost", "selected_by_percent",
]

# Gameweek-level columns kept from merged_gw.csv (subset that is present in all
# three seasons; identity columns are added during assembly).
GW_KEEP_COLS = [
    "round", "fixture", "kickoff_time", "was_home",
    "minutes", "starts", "total_points", "xP",
    "goals_scored", "assists",
    "expected_goals", "expected_assists", "expected_goal_involvements",
    "clean_sheets", "goals_conceded", "expected_goals_conceded",
    "saves", "penalties_saved", "penalties_missed", "own_goals",
    "yellow_cards", "red_cards", "bonus", "bps",
    "influence", "creativity", "threat", "ict_index",
    "value", "selected", "transfers_in", "transfers_out", "transfers_balance",
    "team", "opponent_team", "team_h_score", "team_a_score",
]

# Tolerance for cross-checking players_raw season totals vs gameweek sums.
# Any nonzero diff is *reported*; only diffs above the material thresholds
# below are treated as warnings that warrant attention. players_raw is the
# authoritative season snapshot; merged_gw is the assembled per-GW source, and
# the two occasionally disagree for a player-season in the upstream data.
XCHECK_TOL = 1e-6
MATERIAL_DIFF = {          # per-metric "material" threshold
    "total_points": 1.5,
    "minutes": 30.0,
    "goals_scored": 0.5,
    "assists": 0.5,
}


# --------------------------------------------------------------------------- #
# Ingestion (read-only)
# --------------------------------------------------------------------------- #
def read_players_raw(season: str) -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / season / "players_raw.csv", encoding="utf-8")
    df["code"] = pd.to_numeric(df["code"], errors="raise").astype("int64")
    df["id"] = pd.to_numeric(df["id"], errors="raise").astype("int64")
    df["element_type"] = pd.to_numeric(df["element_type"], errors="raise").astype("int64")
    df["season"] = season
    return df


def read_teams(season: str) -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / season / "teams.csv", encoding="utf-8")
    return df[["id", "name"]].rename(columns={"id": "team_id", "name": "team_name"})


def read_merged_gw(season: str) -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / season / "gws" / "merged_gw.csv", encoding="utf-8")
    df["element"] = pd.to_numeric(df["element"], errors="raise").astype("int64")
    df["season"] = season
    return df


# --------------------------------------------------------------------------- #
# Identity resolution
# --------------------------------------------------------------------------- #
def resolve_common_players(raw_by_season: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Return one row per (season, code) for the codes present in ALL seasons,
    with only genuine players (managers excluded)."""
    player_frames = {}
    for s, df in raw_by_season.items():
        players = df[~df["element_type"].isin(NON_PLAYER_TYPES)].copy()
        player_frames[s] = players

    code_sets = [set(df["code"]) for df in player_frames.values()]
    common_codes = set.intersection(*code_sets)

    frames = []
    for s, df in player_frames.items():
        keep = df[df["code"].isin(common_codes)].copy()
        frames.append(keep)
    out = pd.concat(frames, ignore_index=True)
    return out, sorted(common_codes)


# --------------------------------------------------------------------------- #
# Derived-metric helpers
# --------------------------------------------------------------------------- #
def _per90(numerator: pd.Series, minutes: pd.Series) -> pd.Series:
    return np.where(minutes > 0, numerator / minutes * 90.0, np.nan)


# --------------------------------------------------------------------------- #
# Layer 1: player-season panel (sourced from players_raw)
# --------------------------------------------------------------------------- #
def build_season_panel(common_raw: pd.DataFrame,
                       teams_by_season: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df = common_raw.copy()

    # Coerce all stat columns to numeric.
    for c in SEASON_STAT_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Map team id -> team name (per season).
    team_maps = {s: dict(zip(t["team_id"], t["team_name"]))
                 for s, t in teams_by_season.items()}
    df["team_name"] = df.apply(lambda r: team_maps[r["season"]].get(r["team"]), axis=1)

    df["position"] = df["element_type"].map(POSITION_MAP)
    df["now_cost_m"] = df["now_cost"] / 10.0

    # Derived per-90 and value metrics.
    df["points_per_90"] = _per90(df["total_points"], df["minutes"])
    df["goals_per_90"] = _per90(df["goals_scored"], df["minutes"])
    df["assists_per_90"] = _per90(df["assists"], df["minutes"])
    df["xg_per_90"] = _per90(df["expected_goals"], df["minutes"])
    df["xa_per_90"] = _per90(df["expected_assists"], df["minutes"])
    df["xgi_per_90"] = _per90(df["expected_goal_involvements"], df["minutes"])
    df["points_per_million"] = np.where(
        df["now_cost_m"] > 0, df["total_points"] / df["now_cost_m"], np.nan)

    panel = df.rename(columns={
        "id": "season_element_id",
        "team": "team_id",
    })

    ordered = [
        "code", "season", "season_element_id",
        "web_name", "first_name", "second_name",
        "position", "element_type", "team_id", "team_name", "team_code",
        "minutes", "starts",
        "total_points", "bonus", "bps",
        "goals_scored", "assists",
        "expected_goals", "expected_assists", "expected_goal_involvements",
        "clean_sheets", "goals_conceded", "expected_goals_conceded",
        "saves", "penalties_saved", "penalties_missed", "own_goals",
        "yellow_cards", "red_cards",
        "influence", "creativity", "threat", "ict_index",
        "now_cost_m", "selected_by_percent",
        "points_per_90", "goals_per_90", "assists_per_90",
        "xg_per_90", "xa_per_90", "xgi_per_90",
        "points_per_million",
    ]
    panel = panel[ordered].sort_values(["code", "season"]).reset_index(drop=True)
    return panel


# --------------------------------------------------------------------------- #
# Layer 2: gameweek-level long (sourced from merged_gw)
# --------------------------------------------------------------------------- #
def build_gameweek_long(gw_by_season: dict[str, pd.DataFrame],
                        raw_by_season: dict[str, pd.DataFrame],
                        teams_by_season: dict[str, pd.DataFrame],
                        common_codes: list[int]) -> tuple[pd.DataFrame, dict]:
    common_set = set(common_codes)
    frames = []
    diagnostics = {"unmapped_elements_rows": {}, "rows_before_filter": {},
                   "rows_after_filter": {}}

    for s in SEASONS:
        gw = gw_by_season[s].copy()
        raw = raw_by_season[s]
        id_to_code = dict(zip(raw["id"], raw["code"]))
        team_map = dict(zip(teams_by_season[s]["team_id"],
                            teams_by_season[s]["team_name"]))

        gw["code"] = gw["element"].map(id_to_code)
        diagnostics["rows_before_filter"][s] = int(len(gw))
        diagnostics["unmapped_elements_rows"][s] = int(gw["code"].isna().sum())

        gw = gw[gw["code"].isin(common_set)].copy()
        gw["code"] = gw["code"].astype("int64")
        diagnostics["rows_after_filter"][s] = int(len(gw))

        # Keep declared columns that exist; coerce numerics.
        keep = [c for c in GW_KEEP_COLS if c in gw.columns]
        gw = gw[["season", "code", "name", "position", "element"] + keep].copy()
        gw = gw.rename(columns={"element": "season_element_id",
                                "team": "team_name"})
        gw["opponent_team_name"] = gw["opponent_team"].map(team_map)
        if "value" in gw.columns:
            gw["price_m"] = pd.to_numeric(gw["value"], errors="coerce") / 10.0
        frames.append(gw)

    out = pd.concat(frames, ignore_index=True)
    out = out.sort_values(["code", "season", "round", "fixture"]).reset_index(drop=True)
    return out, diagnostics


# --------------------------------------------------------------------------- #
# Layer 3: roster (one row per player)
# --------------------------------------------------------------------------- #
def build_roster(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for code, g in panel.groupby("code"):
        g = g.set_index("season")
        latest = g.loc["2025-26"]
        pos = {s: g.loc[s, "position"] for s in SEASONS}
        team = {s: g.loc[s, "team_name"] for s in SEASONS}
        minutes = {s: g.loc[s, "minutes"] for s in SEASONS}
        pts_total = float(g["total_points"].sum())
        min_total = float(g["minutes"].sum())
        rows.append({
            "code": int(code),
            "web_name": latest["web_name"],
            "first_name": latest["first_name"],
            "second_name": latest["second_name"],
            "position_2023_24": pos["2023-24"],
            "position_2024_25": pos["2024-25"],
            "position_2025_26": pos["2025-26"],
            "position_changed": len(set(pos.values())) > 1,
            "team_2023_24": team["2023-24"],
            "team_2024_25": team["2024-25"],
            "team_2025_26": team["2025-26"],
            "team_changed": len(set(team.values())) > 1,
            "played_all_seasons": all(m > 0 for m in minutes.values()),
            "points_3yr_total": pts_total,
            "minutes_3yr_total": min_total,
            "points_per_90_3yr": (pts_total / min_total * 90.0) if min_total > 0 else np.nan,
        })
    roster = pd.DataFrame(rows).sort_values(
        "points_3yr_total", ascending=False).reset_index(drop=True)
    return roster


# --------------------------------------------------------------------------- #
# Cross-validation: players_raw season totals vs gameweek sums
# --------------------------------------------------------------------------- #
def cross_check_panel_vs_gw(panel: pd.DataFrame,
                            gw_long: pd.DataFrame) -> tuple[dict, list]:
    """Compare authoritative players_raw season totals against summed
    gameweek data. Returns (per-metric summary, list of exception rows)."""
    check_cols = ["total_points", "minutes", "goals_scored", "assists"]
    gw_sums = (gw_long.groupby(["code", "season"])[check_cols]
               .sum().reset_index()
               .rename(columns={c: f"gw_{c}" for c in check_cols}))
    merged = panel.merge(gw_sums, on=["code", "season"], how="left")

    result = {}
    for c in check_cols:
        diff = (merged[c].fillna(0) - merged[f"gw_{c}"].fillna(0)).abs()
        result[c] = {
            "max_abs_diff": float(diff.max()),
            "mean_abs_diff": float(diff.mean()),
            "rows_mismatched": int((diff > XCHECK_TOL).sum()),
            "rows_material": int((diff > MATERIAL_DIFF[c]).sum()),
        }

    # Enumerate every player-season with ANY nonzero diff (full transparency).
    exceptions = []
    for _, r in merged.iterrows():
        diffs = {c: float(abs((r[c] if pd.notna(r[c]) else 0)
                              - (r[f"gw_{c}"] if pd.notna(r[f"gw_{c}"]) else 0)))
                 for c in check_cols}
        if any(d > XCHECK_TOL for d in diffs.values()):
            exceptions.append({
                "code": int(r["code"]),
                "web_name": r["web_name"],
                "season": r["season"],
                "team_name": r["team_name"],
                **{f"raw_{c}": (float(r[c]) if pd.notna(r[c]) else None) for c in check_cols},
                **{f"gw_{c}": (float(r[f"gw_{c}"]) if pd.notna(r[f"gw_{c}"]) else None) for c in check_cols},
                "abs_diff": diffs,
                "material": any(diffs[c] > MATERIAL_DIFF[c] for c in check_cols),
            })
    return result, exceptions


# --------------------------------------------------------------------------- #
# Validation checkpoint
# --------------------------------------------------------------------------- #
def run_validation(raw_by_season, common_raw, common_codes,
                   panel, gw_long, roster, gw_diag, xcheck, xcheck_exceptions) -> dict:
    hard, diagnostic = [], []

    def add_hard(name, passed, detail):
        hard.append({"check": name, "passed": bool(passed), "detail": detail})

    def add_diag(name, passed, detail):
        diagnostic.append({"check": name, "passed": bool(passed), "detail": detail})

    # -- Hard structural checks (these gate the build) --------------------- #
    for s in SEASONS:
        add_hard(f"players_raw non-empty [{s}]", len(raw_by_season[s]) > 0,
                 {"rows": int(len(raw_by_season[s]))})

    for s in SEASONS:
        players = raw_by_season[s][~raw_by_season[s]["element_type"].isin(NON_PLAYER_TYPES)]
        add_hard(f"code unique within season [{s}]", players["code"].is_unique,
                 {"n_players": int(len(players)), "n_unique_codes": int(players["code"].nunique())})

    n_common = len(common_codes)
    add_hard("common player count > 0", n_common > 0, {"n_common": n_common})

    add_hard("panel row count == n_common * 3",
             len(panel) == n_common * len(SEASONS),
             {"panel_rows": int(len(panel)), "expected": n_common * len(SEASONS)})
    add_hard("panel (code, season) unique",
             not panel.duplicated(["code", "season"]).any(),
             {"duplicated_rows": int(panel.duplicated(["code", "season"]).sum())})
    add_hard("panel has all 3 seasons for every player",
             bool((panel.groupby("code")["season"].nunique() == 3).all()),
             {"players_missing_a_season":
              int((panel.groupby("code")["season"].nunique() != 3).sum())})

    add_hard("roster row count == n_common", len(roster) == n_common,
             {"roster_rows": int(len(roster)), "expected": n_common})
    add_hard("roster code unique", roster["code"].is_unique,
             {"n_unique": int(roster["code"].nunique())})

    bad_pos = sorted(set(panel["position"].dropna()) - {"GK", "DEF", "MID", "FWD"})
    add_hard("panel positions in {GK,DEF,MID,FWD}", len(bad_pos) == 0,
             {"unexpected_positions": bad_pos})

    add_hard("panel: no null code/season",
             not panel[["code", "season"]].isna().any().any(),
             {"null_code": int(panel["code"].isna().sum()),
              "null_season": int(panel["season"].isna().sum())})

    for c in ["minutes", "goals_scored", "assists"]:
        add_hard(f"panel {c} >= 0", bool((panel[c].fillna(0) >= 0).all()),
                 {"min": float(panel[c].min())})

    add_hard("gw_long codes subset of common roster",
             set(gw_long["code"]).issubset(set(common_codes)),
             {"gw_unique_codes": int(gw_long["code"].nunique())})
    add_hard("gw_long: all elements mapped to a code (0 unmapped)",
             all(v == 0 for v in gw_diag["unmapped_elements_rows"].values()),
             gw_diag["unmapped_elements_rows"])

    # -- Soft diagnostics (source cross-check; reported, not gating) ------- #
    for c, r in xcheck.items():
        add_diag(f"xcheck [{c}]: 0 MATERIAL diffs (>{MATERIAL_DIFF[c]})",
                 r["rows_material"] == 0, r)

    n_material = sum(1 for e in xcheck_exceptions if e["material"])
    all_hard_passed = all(c["passed"] for c in hard)
    summary = {
        "n_common_players": n_common,
        "panel_rows": int(len(panel)),
        "gw_rows": int(len(gw_long)),
        "roster_rows": int(len(roster)),
        "all_hard_passed": all_hard_passed,
        "all_diagnostics_clean": all(c["passed"] for c in diagnostic),
        "hard_checks": hard,
        "diagnostic_checks": diagnostic,
        "gw_diagnostics": gw_diag,
        "cross_check": xcheck,
        "cross_check_exceptions": xcheck_exceptions,
        "n_source_discrepancy_rows": len(xcheck_exceptions),
        "n_material_discrepancy_rows": n_material,
    }
    return summary


def write_validation_report(summary: dict) -> None:
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
    (VALIDATION_DIR / "core_dataset_validation.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8")

    lines = ["# Core Dataset Validation Report", ""]
    lines.append(f"- Common players (all 3 seasons): **{summary['n_common_players']}**")
    lines.append(f"- Season panel rows: **{summary['panel_rows']}**")
    lines.append(f"- Gameweek-long rows: **{summary['gw_rows']}**")
    lines.append(f"- Roster rows: **{summary['roster_rows']}**")
    status = "✅ ALL HARD CHECKS PASSED" if summary["all_hard_passed"] else "❌ HARD-CHECK FAILURES"
    lines.append(f"- Structural integrity: **{status}**")
    lines.append(f"- Source discrepancy rows (any nonzero diff): "
                 f"**{summary['n_source_discrepancy_rows']}** "
                 f"(material: **{summary['n_material_discrepancy_rows']}**)")
    lines.append("")
    lines.append("## Hard structural checks (gate the build)")
    lines.append("")
    lines.append("| Check | Result | Detail |")
    lines.append("|---|---|---|")
    for c in summary["hard_checks"]:
        mark = "✅" if c["passed"] else "❌"
        detail = json.dumps(c["detail"])
        if len(detail) > 120:
            detail = detail[:117] + "..."
        lines.append(f"| {c['check']} | {mark} | `{detail}` |")
    lines.append("")
    lines.append("## Source cross-check diagnostics (players_raw vs gameweek-sum)")
    lines.append("")
    lines.append("`players_raw.csv` is the authoritative season snapshot and is the "
                 "source for the season panel. The gameweek layer is faithful to "
                 "`merged_gw.csv`. Where the two upstream files disagree for a "
                 "player-season, it is listed below rather than silently reconciled.")
    lines.append("")
    lines.append("| Metric | max abs diff | mean abs diff | rows w/ any diff | rows material |")
    lines.append("|---|---|---|---|---|")
    for m, r in summary["cross_check"].items():
        lines.append(f"| {m} | {r['max_abs_diff']:.4f} | {r['mean_abs_diff']:.4f} | "
                     f"{r['rows_mismatched']} | {r['rows_material']} |")
    lines.append("")
    if summary["cross_check_exceptions"]:
        lines.append("### Player-seasons with a source discrepancy")
        lines.append("")
        lines.append("| code | player | season | metric | players_raw | gw-sum | abs diff | material |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for e in summary["cross_check_exceptions"]:
            for m, d in e["abs_diff"].items():
                if d > 1e-6:
                    lines.append(
                        f"| {e['code']} | {e['web_name']} | {e['season']} | {m} | "
                        f"{e[f'raw_{m}']:.0f} | {e[f'gw_{m}']:.0f} | {d:.0f} | "
                        f"{'yes' if e['material'] else 'no'} |")
        lines.append("")
    (VALIDATION_DIR / "core_dataset_validation.md").write_text(
        "\n".join(lines), encoding="utf-8")


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
def main() -> None:
    SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)

    print("Ingesting (read-only) ...")
    raw_by_season = {s: read_players_raw(s) for s in SEASONS}
    teams_by_season = {s: read_teams(s) for s in SEASONS}
    gw_by_season = {s: read_merged_gw(s) for s in SEASONS}

    print("Resolving common players (intersection on stable code) ...")
    common_raw, common_codes = resolve_common_players(raw_by_season)
    print(f"  -> {len(common_codes)} players present in all {len(SEASONS)} seasons")

    print("Building season panel ...")
    panel = build_season_panel(common_raw, teams_by_season)

    print("Building gameweek-long layer ...")
    gw_long, gw_diag = build_gameweek_long(
        gw_by_season, raw_by_season, teams_by_season, common_codes)

    print("Building roster ...")
    roster = build_roster(panel)

    print("Cross-checking panel vs gameweek sums ...")
    xcheck, xcheck_exceptions = cross_check_panel_vs_gw(panel, gw_long)

    print("Running validation ...")
    summary = run_validation(raw_by_season, common_raw, common_codes,
                             panel, gw_long, roster, gw_diag, xcheck,
                             xcheck_exceptions)
    write_validation_report(summary)

    # Serialize outputs (scratch only)
    roster_path = SUMMARIES_DIR / "core_players_roster.csv"
    panel_path = SUMMARIES_DIR / "core_player_season_panel.csv"
    gw_path = SUMMARIES_DIR / "core_player_gameweek_long.csv"
    roster.to_csv(roster_path, index=False, encoding="utf-8")
    panel.to_csv(panel_path, index=False, encoding="utf-8")
    gw_long.to_csv(gw_path, index=False, encoding="utf-8")

    manifest = {
        "description": "Core 3-season common-player FPL dataset",
        "seasons": SEASONS,
        "identity_key": "code (stable FPL permanent player code)",
        "common_players": len(common_codes),
        "inputs": {
            s: {
                "players_raw": f"data/{s}/players_raw.csv",
                "merged_gw": f"data/{s}/gws/merged_gw.csv",
                "teams": f"data/{s}/teams.csv",
            } for s in SEASONS
        },
        "outputs": {
            "roster": "scratch/summaries/core_players_roster.csv",
            "season_panel": "scratch/summaries/core_player_season_panel.csv",
            "gameweek_long": "scratch/summaries/core_player_gameweek_long.csv",
        },
        "row_counts": {
            "roster": int(len(roster)),
            "season_panel": int(len(panel)),
            "gameweek_long": int(len(gw_long)),
        },
        "validation": {
            "all_hard_passed": summary["all_hard_passed"],
            "source_discrepancy_rows": summary["n_source_discrepancy_rows"],
            "material_discrepancy_rows": summary["n_material_discrepancy_rows"],
            "report": "scratch/validation/core_dataset_validation.md",
        },
        "non_player_exclusions": "element_type == 5 (Assistant Manager) removed before intersection",
    }
    (SUMMARIES_DIR / "core_dataset_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")

    print()
    print(f"  roster        -> {roster_path.relative_to(REPO_ROOT)}  ({len(roster)} rows)")
    print(f"  season panel  -> {panel_path.relative_to(REPO_ROOT)}  ({len(panel)} rows)")
    print(f"  gameweek long -> {gw_path.relative_to(REPO_ROOT)}  ({len(gw_long)} rows)")
    print(f"  validation    -> scratch/validation/core_dataset_validation.md")
    print(f"  HARD CHECKS PASSED: {summary['all_hard_passed']}  |  "
          f"source-discrepancy rows: {summary['n_source_discrepancy_rows']} "
          f"(material: {summary['n_material_discrepancy_rows']})")
    if not summary["all_hard_passed"]:
        raise SystemExit("Hard validation checks failed — see report.")


if __name__ == "__main__":
    main()
