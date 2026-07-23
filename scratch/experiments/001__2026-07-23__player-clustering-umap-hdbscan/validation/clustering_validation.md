# Clustering validation

- Seed: 42 · min_minutes: 900 · K_coarse: 5
- Features (23): goals_scored, assists, expected_goals, expected_assists, expected_goal_involvements, clean_sheets, goals_conceded, expected_goals_conceded, saves, bonus, bps, yellow_cards, red_cards, influence, creativity, threat, ict_index, points_per_90, goals_per_90, assists_per_90, xg_per_90, xa_per_90, xgi_per_90
- Assignment rows: 674 (expected 674, match: True)
- Coarse nested in fine: True
- No NaN in clustered features: True

| Season | Clustered | Excluded(<min) | Level | Clusters | Noise | Silhouette |
|---|---|---|---|---|---|---|
| 2023-24 | 237 | 152 | coarse | 5 | 9 | 0.273 |
| 2023-24 | 237 | 152 | fine | 9 | 9 | 0.495 |
| 2024-25 | 229 | 160 | coarse | 5 | 29 | 0.452 |
| 2024-25 | 229 | 160 | fine | 8 | 29 | 0.473 |
| 2025-26 | 208 | 181 | coarse | 5 | 9 | 0.577 |
| 2025-26 | 208 | 181 | fine | 7 | 9 | 0.556 |