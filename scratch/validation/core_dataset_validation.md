# Core Dataset Validation Report

- Common players (all 3 seasons): **389**
- Season panel rows: **1167**
- Gameweek-long rows: **42989**
- Roster rows: **389**
- Structural integrity: **✅ ALL HARD CHECKS PASSED**
- Source discrepancy rows (any nonzero diff): **1** (material: **0**)

## Hard structural checks (gate the build)

| Check | Result | Detail |
|---|---|---|
| players_raw non-empty [2023-24] | ✅ | `{"rows": 865}` |
| players_raw non-empty [2024-25] | ✅ | `{"rows": 804}` |
| players_raw non-empty [2025-26] | ✅ | `{"rows": 841}` |
| code unique within season [2023-24] | ✅ | `{"n_players": 865, "n_unique_codes": 865}` |
| code unique within season [2024-25] | ✅ | `{"n_players": 784, "n_unique_codes": 784}` |
| code unique within season [2025-26] | ✅ | `{"n_players": 841, "n_unique_codes": 841}` |
| common player count > 0 | ✅ | `{"n_common": 389}` |
| panel row count == n_common * 3 | ✅ | `{"panel_rows": 1167, "expected": 1167}` |
| panel (code, season) unique | ✅ | `{"duplicated_rows": 0}` |
| panel has all 3 seasons for every player | ✅ | `{"players_missing_a_season": 0}` |
| roster row count == n_common | ✅ | `{"roster_rows": 389, "expected": 389}` |
| roster code unique | ✅ | `{"n_unique": 389}` |
| panel positions in {GK,DEF,MID,FWD} | ✅ | `{"unexpected_positions": []}` |
| panel: no null code/season | ✅ | `{"null_code": 0, "null_season": 0}` |
| panel minutes >= 0 | ✅ | `{"min": 0.0}` |
| panel goals_scored >= 0 | ✅ | `{"min": 0.0}` |
| panel assists >= 0 | ✅ | `{"min": 0.0}` |
| gw_long codes subset of common roster | ✅ | `{"gw_unique_codes": 389}` |
| gw_long: all elements mapped to a code (0 unmapped) | ✅ | `{"2023-24": 0, "2024-25": 0, "2025-26": 0}` |

## Source cross-check diagnostics (players_raw vs gameweek-sum)

`players_raw.csv` is the authoritative season snapshot and is the source for the season panel. The gameweek layer is faithful to `merged_gw.csv`. Where the two upstream files disagree for a player-season, it is listed below rather than silently reconciled.

| Metric | max abs diff | mean abs diff | rows w/ any diff | rows material |
|---|---|---|---|---|
| total_points | 1.0000 | 0.0009 | 1 | 0 |
| minutes | 17.0000 | 0.0146 | 1 | 0 |
| goals_scored | 0.0000 | 0.0000 | 0 | 0 |
| assists | 0.0000 | 0.0000 | 0 | 0 |

### Player-seasons with a source discrepancy

| code | player | season | metric | players_raw | gw-sum | abs diff | material |
|---|---|---|---|---|---|---|---|
| 487117 | Ferguson | 2024-25 | total_points | 28 | 27 | 1 | no |
| 487117 | Ferguson | 2024-25 | minutes | 385 | 368 | 17 | no |
