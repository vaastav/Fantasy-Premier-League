# Core 3-Season Common-Player Dataset — Data Dictionary

**Scope:** FPL seasons **2023-24, 2024-25, 2025-26**, restricted to the
**389 players present in all three seasons**.

**Built by:** `scratch/experiments/build_core_dataset.py`
**Validated by:** `scratch/validation/core_dataset_validation.md`

## Identity & inclusion rules

- **Join key = `code`** — the permanent, per-person FPL player code. It is stable
  across seasons. The per-season `id` / `element` numbers are *reused* each
  season and are **not** valid cross-season keys (they appear here only as
  `season_element_id` for tracing back to the source).
- A player is included **iff** their `code` appears in `players_raw.csv` for
  **all three** seasons. Players who left before 2025-26 or joined after 2023-24
  are excluded.
- **Managers excluded:** `element_type == 5` (Assistant Manager chip entries,
  present only in 2024-25) are removed before the intersection.

## Provenance

| Layer | Source of truth |
|---|---|
| Season aggregates (panel, roster) | `data/<season>/players_raw.csv` (official FPL season snapshot) |
| Gameweek rows | `data/<season>/gws/merged_gw.csv` |
| Team names | `data/<season>/teams.csv` (`id`→`name`; verified consistent with stable `team_code`) |

The season panel (from `players_raw`) was cross-checked against the sum of the
gameweek layer. Goals and assists reconcile exactly for all 1,167 player-seasons.
One player-season (Ferguson, 2024-25) differs by 1 point / 17 minutes between the
two upstream files — this is an upstream data quirk, reported in the validation
report and **not** silently altered.

---

## File 1 — `core_players_roster.csv` (389 rows, one per player)

The canonical player list. Latest-season identity plus 3-year rollups and
change flags.

| Column | Type | Description |
|---|---|---|
| `code` | int | **Primary key.** Permanent FPL player code. |
| `web_name` | str | Display name (from 2025-26). |
| `first_name`, `second_name` | str | Full name (from 2025-26). |
| `position_2023_24/24_25/25_26` | str | Position each season: GK/DEF/MID/FWD. |
| `position_changed` | bool | True if position differs across the 3 seasons. |
| `team_2023_24/24_25/25_26` | str | Club each season. |
| `team_changed` | bool | True if club differs across the 3 seasons. |
| `played_all_seasons` | bool | True if minutes > 0 in every season. |
| `points_3yr_total` | float | Sum of `total_points` over the 3 seasons. |
| `minutes_3yr_total` | float | Sum of `minutes` over the 3 seasons. |
| `points_per_90_3yr` | float | 3-yr points ÷ 3-yr minutes × 90 (NaN if 0 min). |

Sorted by `points_3yr_total` descending.

---

## File 2 — `core_player_season_panel.csv` (1,167 rows = 389 × 3)

One row per **(player, season)**. Season-total stats + derived rates. This is
the primary analysis table for season-over-season work.

**Keys:** `code` + `season` (unique together).

| Column | Type | Description |
|---|---|---|
| `code` | int | Player key. |
| `season` | str | `2023-24` / `2024-25` / `2025-26`. |
| `season_element_id` | int | That season's FPL `id`/`element` (for tracing to source only). |
| `web_name`, `first_name`, `second_name` | str | Name *as recorded that season*. |
| `position` | str | GK/DEF/MID/FWD that season. |
| `element_type` | int | Raw FPL position code (1–4). |
| `team_id` | int | Season team id. |
| `team_name` | str | Club that season. |
| `team_code` | int | Stable club code. |
| `minutes`, `starts` | num | Appearance volume. |
| `total_points`, `bonus`, `bps` | num | Scoring. |
| `goals_scored`, `assists` | num | Attacking returns. |
| `expected_goals`, `expected_assists`, `expected_goal_involvements` | num | Season xG / xA / xGI. |
| `clean_sheets`, `goals_conceded`, `expected_goals_conceded` | num | Defensive. |
| `saves`, `penalties_saved`, `penalties_missed`, `own_goals` | num | Keeper / misc. |
| `yellow_cards`, `red_cards` | num | Discipline. |
| `influence`, `creativity`, `threat`, `ict_index` | float | FPL ICT components. |
| `now_cost_m` | float | End-of-season price in £m (`now_cost` ÷ 10). |
| `selected_by_percent` | float | End-of-season ownership %. |
| `points_per_90` | float | `total_points` ÷ minutes × 90 (NaN if 0 min). |
| `goals_per_90`, `assists_per_90` | float | Per-90 rates. |
| `xg_per_90`, `xa_per_90`, `xgi_per_90` | float | Per-90 expected rates. |
| `points_per_million` | float | `total_points` ÷ `now_cost_m` (value metric). |

---

## File 3 — `core_player_gameweek_long.csv` (42,989 rows, one per player-gameweek)

One row per player **per gameweek appearance**. Double-gameweeks yield multiple
rows in the same `round` (one per fixture). Faithful to `merged_gw.csv`, filtered
to the 389 players, with `code`, `season`, and mapped opponent name added.

**Keys:** `code` + `season` + `round` + `fixture`.

| Column | Type | Description |
|---|---|---|
| `season` | str | Season label. |
| `code` | int | Player key (mapped from `element`). |
| `name` | str | Player name as in the GW file. |
| `position` | str | GK/DEF/MID/FWD. |
| `season_element_id` | int | Season `element` id. |
| `round` | int | Gameweek (1–38). |
| `fixture` | int | Season fixture id. |
| `kickoff_time` | str | ISO timestamp. |
| `was_home` | bool | Home fixture flag. |
| `minutes`, `starts` | num | Appearance. |
| `total_points`, `xP` | num | Actual and expected points. |
| `goals_scored`, `assists` | num | Returns. |
| `expected_goals`, `expected_assists`, `expected_goal_involvements` | num | Per-GW expected. |
| `clean_sheets`, `goals_conceded`, `expected_goals_conceded` | num | Defensive. |
| `saves`, `penalties_saved`, `penalties_missed`, `own_goals` | num | Keeper / misc. |
| `yellow_cards`, `red_cards`, `bonus`, `bps` | num | Discipline / bonus. |
| `influence`, `creativity`, `threat`, `ict_index` | float | ICT components. |
| `value` | int | Price at that GW, in tenths of £m. |
| `price_m` | float | Price at that GW in £m (`value` ÷ 10). |
| `selected` | int | Selection count. |
| `transfers_in`, `transfers_out`, `transfers_balance` | int | GW transfer flows. |
| `team_name` | str | Player's club (from the GW file `team`). |
| `opponent_team` | int | Opponent season team id. |
| `opponent_team_name` | str | Opponent club name (mapped via `teams.csv`). |
| `team_h_score`, `team_a_score` | num | Final score. |

---

## Usage notes

- Join across layers on `code` (+ `season` for panel, `+ round/fixture` for GW).
- `now_cost_m` / `price_m` are the **only** monetary fields already converted to
  £m; the raw `value` remains in tenths for fidelity.
- Per-90 columns are `NaN` (not 0) when a player logged 0 minutes that season —
  handle explicitly before ranking on rate stats.
- To restrict to players who actually featured every season, filter roster on
  `played_all_seasons == True`.
