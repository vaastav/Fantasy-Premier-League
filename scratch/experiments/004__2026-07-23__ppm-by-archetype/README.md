# Experiment 004 — ppm-by-archetype

> **Status:** complete · **Created:** 2026-07-23 · **Author:** andrew · **Depends on:** 002

## Question

Which archetypes deliver the best FPL value — points per £m (PPM)?

## Method

Consume `exp 002/player_archetypes.csv` (classified players, `now_cost_m > 0`).
PPM = `total_points / now_cost_m` (end-of-season price). Aggregate PPM per
archetype (pooled and per season); boxplot ordered by median.

## Results

Median PPM by archetype (pooled; overall median 15.8):

| Archetype | median PPM | n | mean pts | mean £m |
|---|---|---|---|---|
| Elite playmaker | 24.0 | 17 | 142 | 6.1 |
| Elite goalscorer | 23.0 | 90 | 160 | 7.4 |
| Goalkeeper | 21.4 | 68 | 100 | 4.7 |
| Attacking / ball-playing defender | 20.2 | 162 | 100 | 4.9 |
| Creative midfielder | 19.8 | 58 | 118 | 6.2 |
| Balanced defender | 16.1 | 105 | 77 | 4.8 |
| Premium attacker | 15.4 | 133 | 88 | 5.7 |
| Rotation midfielder | 10.7 | 124 | 59 | 5.1 |
| Defensive / rotation defender | 10.0 | 177 | 44 | 4.4 |

See `outputs/ppm_by_archetype.csv`, `ppm_by_archetype_season.csv`, and the
boxplot in `outputs/figures/`.

## Interpretation

- **Elite playmakers and elite goalscorers** are the best value despite premium
  prices — their point hauls outpace their cost.
- **Goalkeepers and attacking/ball-playing defenders** are the value sweet spot:
  cheap (£4.7–4.9m) yet ~100 points.
- **Rotation midfielders and defensive/rotation defenders** are the worst value —
  priced like contributors but returning few points.

**Caveats:** PPM uses end-of-season price (`now_cost`), which drifts from the
purchase price a manager actually paid; it rewards players who stayed cheap.
Survivorship: only ≥900-min players are included, so genuine "cheap benchwarmer"
traps are excluded. Archetype membership itself carries exp 002's caveats.

## Conclusion

**Keep.** A clean value ranking by archetype; pairs naturally with 003
(transitions) — e.g. buying Premium attackers likely to transition to Elite.

## Provenance
- Depends on exp 002 outputs. Core `core_v1`. Git commit in `manifest.json`.
