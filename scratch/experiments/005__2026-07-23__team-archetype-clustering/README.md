# Experiment 005 — team-archetype-clustering

> **Status:** complete · **Created:** 2026-07-23 · **Author:** andrew · **Depends on:** 002

## Question

If we describe each team-season by the archetype makeup of its qualifying squad,
do teams fall into distinct compositional styles?

## Method

Consume `exp 002/player_archetypes.csv`. For each **team-season** (20 teams × 3 =
60), compute — over its classified (≥900-min) players — the **count** and
**proportion** of each of the 9 canonical archetypes (18 features). Standardize.

Primary clustering: **agglomerative**, K chosen by silhouette over K=3–7.
HDBSCAN is run as a density robustness check and stored in
`team_cluster_hdbscan`.

## Results

- 60 team-seasons, 18 features.
- **Agglomerative:** best K=7 but silhouette only **0.16** — weak separation.
- **HDBSCAN:** 2 clusters + 1 noise — i.e. one dominant blob.
- Both point to the same conclusion: team compositions are a **continuum**, not
  cleanly separable clusters. Still, the K=7 partition surfaces interpretable
  tendencies: a defender-heavy group (~43% defensive defenders), an
  elite-attacker group (high Elite goalscorer share), and an attack-heavy group
  (~33% attacking defenders).

See `outputs/team_archetype_features.csv`, `team_clusters.csv`,
`team_cluster_profiles.csv`, and `outputs/figures/team_clusters.png`.

## Interpretation

Teams don't split into sharply distinct "system" clusters on archetype makeup —
most Premier League squads carry a similar spread of roles, differing by degree.
The partition is descriptive, not definitive.

**Important caveat — season leakage:** the clusters partly track *season* rather
than pure team identity, because canonical archetype prevalence shifts year to
year (2 archetypes are not present in all seasons; proportions rebase
accordingly). A cleaner follow-up would standardize archetype proportions
*within season* before clustering, or restrict to the 7 all-season archetypes.

Also: composition ignores player *quality within* an archetype and squad depth
beyond the ≥900-min cohort.

## Conclusion

**Keep, with caveats.** Deliverable is the team-season archetype-composition
table plus a weak descriptive partition. The headline finding is itself useful:
teams are compositionally continuous. Recommended follow-up: within-season
normalization and/or proportions-only features to remove season leakage.

## Provenance
- Depends on exp 002 outputs. Core `core_v1`. Git commit in `manifest.json`.
