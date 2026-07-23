# Experiment 003 — archetype-transitions

> **Status:** complete · **Created:** 2026-07-23 · **Author:** andrew · **Depends on:** 002

## Question

Which players change archetype from one season to the next, and what are the most
common role transitions?

## Method

Consume `exp 002/player_archetypes.csv`. For each consecutive season pair
(2023-24→2024-25, 2024-25→2025-26), keep players **classified in both** seasons
(≥900 min, not HDBSCAN noise) and record from→to archetype. Build transition
matrices, a stayed/changed summary, and the most common change types.

## Results

- **358 player-pairs** with a transition. **Overall 35% kept the same fine
  archetype** season to season (38.8% then 31.7%).
- Top role changes are all **adjacent-tier moves within a role**:
  Creative midfielder → Elite goalscorer (18), Attacking↔Balanced↔Defensive
  defender (many), Elite goalscorer → Premium attacker (13).

See `outputs/transitions_long.csv` (per player), `transition_matrix_*.csv`,
`top_changes.csv`, and the heatmaps in `outputs/figures/`.

## Interpretation

Fine archetypes are **quality-tiered**, so most "changes" are players sliding
one tier up/down within the same role as their output fluctuates — not wholesale
role switches. The low 35% stay-rate reflects this tier sensitivity, not
instability of the archetype scheme. Genuine cross-role moves (e.g. a defender
becoming an attacker) are rare.

**Caveats:** only players present ≥900 min in both seasons appear; players moving
in/out of the noise bucket are excluded. Cross-season archetype comparability
relies on exp 002's alignment (2 rarer archetypes are less stable).

## Conclusion

**Keep.** Provides a per-player role-trajectory table and transition matrices for
future work (e.g. predicting breakouts = Premium→Elite transitions).

## Provenance
- Depends on exp 002 outputs. Core `core_v1`. Git commit in `manifest.json`.
