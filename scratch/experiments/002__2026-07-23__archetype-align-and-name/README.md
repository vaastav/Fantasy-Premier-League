# Experiment 002 — archetype-align-and-name

> **Status:** complete · **Created:** 2026-07-23 · **Author:** andrew · **Depends on:** 001
>
> Re-fit fine archetypes on all ≥900-min players and align them across seasons
> into stable, named labels for downstream use.

## Question

Can we turn the per-season fine clusters (whose ids are not comparable across
seasons) into a single set of **stable, human-named archetypes** that apply to
*every* qualifying player-season — the labeled foundation for transitions,
value analysis, and team composition?

## Rationale

Exp 001 clustered only the 389 core players and its cluster ids reset each
season. Downstream work (transitions, PPM, team makeup) needs (a) coverage of
**all** qualifying players, not just ever-presents, and (b) labels that mean the
same thing across seasons. This experiment produces that.

## Method

- **Population:** `scratch/summaries/all_players_season_panel.csv` (all players,
  per season), filtered to **≥ 900 minutes** — 339 / 321 / 339 players.
- **Per-season fine clustering:** same recipe as exp 001 — standardize 23
  production/rate features → UMAP(10-D, `n_neighbors=12`) → HDBSCAN(`leaf`,
  `min_cluster_size=15`). Yields 10-11 fine clusters per season.
- **Cross-season alignment:** take each per-season cluster's centroid (mean raw
  features), pool all 32 centroids, standardize, and **meta-cluster** them
  (Agglomerative, `N=9`) into canonical archetypes. Every player inherits the
  canonical archetype of their season-cluster. `N=9` maximised cross-season
  coverage (7 of 9 archetypes appear in all three seasons).
- **Naming:** each archetype is assigned a base **role** (GK / ATT / DEF / MID)
  from its position mix and goal threat, then a **tier** by ranking within the
  role (e.g. attackers by goals/90, defenders by threat, mids by creativity).
  This gives distinct, ordered names deterministically.
- Seed = 42. The `all_players_season_panel.csv` sha256 is pinned in
  `manifest.json` (`all_players_panel_sha256`) alongside the `core_v1` pin.

## Results

**9 canonical archetypes** (999 player-seasons labeled; 65 unclassified = HDBSCAN
noise). 7 appear in all three seasons; 2 creative-mid tiers are rarer
(`seasons_present` flags this in `archetype_profiles.csv`).

| Archetype | Role | n | goals/90 | creativity | threat | mean pts | seasons |
|---|---|---|---|---|---|---|---|
| Elite goalscorer | ATT | 90 | 0.41 | 646 | 875 | 160 | 3 |
| Premium attacker | ATT | 133 | 0.31 | 331 | 471 | 88 | 3 |
| Elite playmaker | MID | 17 | 0.18 | 1068 | 475 | 142 | 1 |
| Creative midfielder | MID | 58 | 0.22 | 699 | 532 | 118 | 2 |
| Rotation midfielder | MID | 124 | 0.08 | 225 | 168 | 59 | 3 |
| Attacking / ball-playing defender | DEF | 162 | 0.07 | 353 | 236 | 101 | 3 |
| Balanced defender | DEF | 105 | 0.08 | 280 | 201 | 77 | 3 |
| Defensive / rotation defender | DEF | 177 | 0.03 | 126 | 83 | 44 | 3 |
| Goalkeeper | GK | 68 | 0.00 | 13 | 1 | 100 | 3 |

Spot-checks (2024-25): Elite goalscorer = Salah, Haaland, Palmer, Isak, Mbeumo;
B.Fernandes = Creative midfielder; Virgil = Attacking/ball-playing defender;
Pickford = Goalkeeper. Archetypes recover role + quality tier without position
as a feature.

## Interpretation

The fine archetypes encode both **role and quality tier** (elite vs premium
attacker; attacking vs defensive defender). Meta-clustering the centroids gives
consistent labels across seasons; the two rarer creative-mid tiers reflect
genuine season-to-season variation in how many elite creators cluster distinctly.

**Caveats:** 65 players fall in HDBSCAN noise and are `Unclassified` (borderline
profiles, e.g. Gabriel 2024-25). The 2 low-`seasons_present` archetypes should be
treated cautiously in cross-season comparisons. Names are descriptive shorthands,
not official positions.

## Conclusion

**Keep.** `outputs/player_archetypes.csv` (labeled, all qualifying players) is the
foundation for exp 003 (transitions), 004 (PPM by archetype), 005 (team makeup).
Downstream should join on `code`+`season` and use `archetype_name`.

## Provenance

- Core: `core_v1`; all-players panel sha256 pinned in `manifest.json`.
- Git commit at completion: see `manifest.json`.
