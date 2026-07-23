# Experiment 001 — player-clustering-umap-hdbscan

> **Status:** complete · **Created:** 2026-07-23 · **Author:** andrew
>
> One-line rationale: discover coarse and fine-grained player archetypes from
> season-aggregate stats, per season, unsupervised.

## Question

Do FPL players fall into interpretable **archetypes** based on their
season-aggregate production/style profile, and can we describe them at two
granularities — a few **coarse** role-groups and a richer set of **fine**
sub-roles — consistently across the last three seasons?

## Rationale

A stable archetype label per player-season is a reusable building block: it lets
later experiments condition on player *type* (e.g. "how do creative playmakers
age?", "which archetype offers best points-per-million?") instead of raw stats.
This is the first experiment on the core dataset, so it also exercises the
workflow end-to-end.

## Method

- **Population:** the 389-player core dataset, per season. Restricted to
  players with **≥ 900 minutes** (~10 full matches). Rationale: the season
  minutes distribution is heavily left-spread (mean 1321, std 1124 over all
  player-seasons; 221 have 0 minutes), so an unfiltered clustering — or a
  symmetric mean ± 2σ band, which spans `[0, 3569]` and filters nothing —
  simply recovers a *played-vs-didn't-play* split. A minutes floor removes the
  fringe while keeping elite ever-presents (Salah etc.), and guarantees a
  reliable per-90 denominator.
- **Features (23):** counting production (goals, assists, xG, xA, xGI, clean
  sheets, goals conceded, xGC, saves, bonus, bps, cards), involvement indices
  (influence, creativity, threat, ICT), and per-90 rates (points, goals,
  assists, xG, xA, xGI). **Minutes/starts deliberately excluded** so clustering
  reflects style, not availability. Standardized (z-score) per season.
- **Fine clustering:** UMAP → 10-D embedding (`n_neighbors=12`, `min_dist=0`)
  then HDBSCAN (`min_cluster_size=15`, `min_samples=3`, `leaf`).
- **Coarse clustering:** the fine-cluster centroids (in standardized feature
  space) are agglomerated into **K=5** groups. Coarse is therefore *nested* in
  fine (each fine cluster ⊂ exactly one coarse cluster).
- **Why nested rather than two HDBSCAN runs:** a second HDBSCAN tuned "coarse"
  was unstable across seasons (2024-25 collapsed to 2 clusters while others gave
  6-7). Merging fine centroids is stable, keeps goalkeepers as their own group,
  and yields a clean hierarchy.
- A separate 2-D UMAP is computed **only for visualization**.
- Seed = 42 throughout (UMAP `random_state`), so runs are reproducible.

## How to run

```bash
python scratch/experiments/001__2026-07-23__player-clustering-umap-hdbscan/run.py
# outputs -> ./outputs/   validation -> ./validation/
```

## Results

Players clustered per season: 237 / 229 / 208 (2023-24 / 24-25 / 25-26).

| Season | Coarse (k) | Coarse silhouette | Fine (k) | Fine silhouette | Fine noise |
|---|---|---|---|---|---|
| 2023-24 | 5 | 0.27 | 9 | 0.50 | 9 |
| 2024-25 | 5 | 0.45 | 8 | 0.47 | 29 |
| 2025-26 | 5 | 0.58 | 7 | 0.56 | 9 |

**Coarse archetypes (stable all 3 seasons):** goalkeepers · elite
attackers/goalscorers · creative attacking midfielders · attacking defenders /
full-backs · defensive defenders & rotation. Goalkeepers always separate cleanly
(they form a distinct island in the embedding).

**Fine archetypes** split those further, e.g. for 2024-25:
- f0 goalkeepers (Pickford, Raya) — 93 mean saves
- f3 elite goalscorers (Salah, Palmer, Isak) — highest goals/90 (0.45) & threat
- f2 creative playmakers (B.Fernandes, Semenyo) — highest creativity
- f1 attacking full-backs (Cucurella, Aït-Nouri) — DEF with high creativity
- f4 solid centre-backs (Virgil, Murillo)
- f6 defensive/rotation defenders (Cash, Emerson) — low output, low clean sheets
- f7 rotation forwards + backup keepers (Beto, Muniz)

See `outputs/cluster_profiles.csv` for per-cluster feature means, position mix,
and exemplars; `outputs/figures/` for the UMAP scatter plots.

## Interpretation

The archetypes recover football-sensible roles without ever seeing position as
a feature — position emerges from the stat profile, a good sanity check. Coarse
is genuinely coarse and consistent; fine captures useful sub-roles
(goalscorer vs playmaker; attacking vs defensive full-back). The 2024-25 fine
noise (29) is higher — mostly versatile/rotation players between roles.

**Caveats:** UMAP+HDBSCAN labels are not canonical ground truth — they depend on
the feature set, the minutes floor, and hyperparameters. Cluster *ids* are not
comparable across seasons (re-fit each season); use the profiles to align
archetypes by meaning, not by number. Silhouette on the coarse level for
2023-24 is modest (0.27), reflecting a more continuous outfield manifold.

## Conclusion

**Keep.** The pipeline yields stable, interpretable coarse (5) and fine (7-9)
archetypes per season, nested and reproducible. Outputs (`player_clusters.csv`)
are ready for downstream experiments to consume via `depends_on: ["001"]`.

Natural follow-ups: (a) align archetypes across seasons into stable named
labels; (b) archetype transition analysis (which players move roles season to
season); (c) points-per-million by archetype. Also worth a variant experiment:
sensitivity to the minutes floor and feature set.

## Provenance

- Core dataset: `core_v1` (fingerprint pinned in `manifest.json`)
- Git commit at completion: see `manifest.json`
