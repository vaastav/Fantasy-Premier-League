# Experiment Log — Core 3-Season Common-Player Dataset

**Date:** 2026-07-21
**Author:** agent-assisted (see build script)
**Script:** `scratch/experiments/build_core_dataset.py`
**Run command (from repo root):** `python scratch/experiments/build_core_dataset.py`

## Objective

Create the project's core working dataset: the last three FPL seasons
(2023-24, 2024-25, 2025-26) parsed down to the set of players present in **all
three** seasons (a departure in 2025-26 or an arrival in 2024-25 excludes the
player).

## Inputs (read-only)

For each season in {2023-24, 2024-25, 2025-26}:

- `data/<season>/players_raw.csv` — official season snapshot; source for season aggregates + `code`.
- `data/<season>/gws/merged_gw.csv` — per-gameweek detail.
- `data/<season>/teams.csv` — team id → name mapping.

## Key decisions & assumptions

1. **Cross-season identity = `code`.** Verified that per-season `id`/`element`
   are reused across seasons (Balogun `id=1` in 2023-24 vs Fábio Vieira `id=1`
   in 2024-25), so only the permanent `code` joins players correctly. Confirmed
   `code` is unique within every season and maps to a consistent person (52
   codes had cosmetic name spelling differences only, e.g. accents).
2. **"Present" = registered in `players_raw` that season** (squad membership),
   matching the user's transfer-based definition. A `played_all_seasons` flag
   (minutes > 0 each season) is provided for stricter filtering without
   dropping anyone from the core set.
3. **Managers excluded.** `element_type == 5` (Assistant Manager, only in
   2024-25, 20 entries) removed before intersection. Verified zero leak into
   the common set.
4. **Season panel sourced from `players_raw`** (authoritative), then
   cross-checked against summed gameweek data.
5. **Team names mapped via season `teams.csv`** (`id`→`name`); verified this
   agrees with the stable `team_code`→name mapping for all 1,167 rows.

## Outputs (written under scratch/ only)

- `scratch/summaries/core_players_roster.csv` — 389 rows
- `scratch/summaries/core_player_season_panel.csv` — 1,167 rows
- `scratch/summaries/core_player_gameweek_long.csv` — 42,989 rows
- `scratch/summaries/core_dataset_manifest.json` — provenance manifest
- `scratch/summaries/CORE_DATASET_DICTIONARY.md` — schema documentation
- `scratch/validation/core_dataset_validation.{json,md}` — validation report

## Results

- **389 players** present in all three seasons (per-season totals: 865 / 804 / 841).
- Pairwise overlaps: 23-24 ∩ 24-25 = 513; 24-25 ∩ 25-26 = 534; 23-24 ∩ 25-26 = 432.
- **All hard structural checks passed** (row counts, key uniqueness, position
  domain, null keys, GW→code mapping, subset integrity).
- **Cross-check vs gameweek sums:** goals & assists reconcile exactly for all
  1,167 player-seasons. One player-season (Ferguson, 2024-25) differs by
  1 point / 17 minutes between `players_raw` and the GW files — an upstream data
  quirk, flagged as non-material, not altered.

## Spot-checks (sanity)

- Top 3-yr scorer: M.Salah (678), then Haaland (637), Watkins (581) — as expected.
- Salah season line matches reality (211 → 344 → 123 pts; 2024-25 was his record year).
- Real transfers correctly reflected: Isak → Liverpool, Mbeumo & Cunha → Man Utd (25-26).
- Note: the 2025-26 source records **Antoine Semenyo at Man City** (team_id 13 /
  team_code 43, identical to Haaland). This is faithful to `data/` — flagged here
  as a source characteristic to be aware of, not a pipeline error.

## Reproduce

```bash
cd <repo root>
python scratch/experiments/build_core_dataset.py
# outputs -> scratch/summaries/, validation -> scratch/validation/
```

## Possible next steps

- Add a `played_all_seasons`-only convenience view if downstream analysis needs it.
- Join fixtures/FDR for schedule-adjusted metrics.
- Feature engineering (form windows, per-90 z-scores) as a separate stage that
  consumes these validated summaries — never the raw data directly.
