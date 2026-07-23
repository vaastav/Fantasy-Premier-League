"""Experiment 002 (archetype-align-and-name).

Extends exp 001's fine archetype clustering to ALL >=900-minute players per
season (using scratch/summaries/all_players_season_panel.csv), then ALIGNS the
per-season fine clusters across seasons into a single set of stable, named
canonical archetypes.

Pipeline
--------
1. Per season: standardize 23 production/rate features -> UMAP(10D) ->
   HDBSCAN(leaf) => per-season fine clusters (same recipe as exp 001).
2. Compute each per-season cluster's centroid (mean raw features).
3. Pool all centroids across seasons, standardize, and meta-cluster them
   (Agglomerative, N_ARCHETYPES) => canonical archetype id per season-cluster.
4. Every player inherits the canonical archetype of their season-cluster.
5. Auto-name each canonical archetype from its aggregated profile.

Outputs (this experiment only):
- outputs/player_archetypes.csv     one row per qualifying player-season, labeled
- outputs/archetype_profiles.csv    canonical archetype profiles (feature means)
- outputs/season_cluster_map.csv    per-season cluster -> canonical archetype
- outputs/figures/                  per-season UMAP colored by canonical archetype

Run from repo root:
    python scratch/experiments/002__2026-07-23__archetype-align-and-name/run.py
"""

from __future__ import annotations

import json
import sys
import pathlib

import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _lib import experiment as exp  # noqa: E402

SEED = 42
SEASONS = ["2023-24", "2024-25", "2025-26"]
MIN_MINUTES = 900
N_ARCHETYPES = 9           # canonical (cross-season) fine archetypes

ALL_PANEL = exp.SUMMARIES / "all_players_season_panel.csv"

FEATURES = [
    "goals_scored", "assists", "expected_goals", "expected_assists",
    "expected_goal_involvements",
    "clean_sheets", "goals_conceded", "expected_goals_conceded", "saves",
    "bonus", "bps", "yellow_cards", "red_cards",
    "influence", "creativity", "threat", "ict_index",
    "points_per_90", "goals_per_90", "assists_per_90",
    "xg_per_90", "xa_per_90", "xgi_per_90",
]
CONTEXT = ["total_points", "now_cost_m", "selected_by_percent", "minutes"]

UMAP_CLUSTER = {"n_neighbors": 12, "min_dist": 0.0, "n_components": 10}
UMAP_VIZ = {"n_neighbors": 15, "min_dist": 0.10, "n_components": 2}
HDBSCAN_FINE = {"min_cluster_size": 15, "min_samples": 3,
                "cluster_selection_method": "leaf"}


def cluster_season(X: pd.DataFrame):
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import HDBSCAN
    import umap
    Xs = StandardScaler().fit_transform(X.values)
    emb = umap.UMAP(random_state=SEED, metric="euclidean", **UMAP_CLUSTER).fit_transform(Xs)
    labels = HDBSCAN(**HDBSCAN_FINE).fit_predict(emb)
    viz = umap.UMAP(random_state=SEED, metric="euclidean", **UMAP_VIZ).fit_transform(Xs)
    return labels, viz


# Base role -> ordered tier vocabulary (best/most-attacking first) and the metric
# used to rank archetypes within the role.
ROLE_VOCAB = {
    "GK":  (["Goalkeeper"], "mean_total_points"),
    "ATT": (["Elite goalscorer", "Premium attacker", "Secondary attacker",
             "Squad attacker"], "mean_goals_per_90"),
    "DEF": (["Attacking / ball-playing defender", "Balanced defender",
             "Defensive / rotation defender", "Deep rotation defender"], "mean_threat"),
    "MID": (["Elite playmaker", "Creative midfielder", "Rotation midfielder",
             "Deep-lying midfielder"], "mean_creativity"),
}


def base_role(prof: dict) -> str:
    if prof["pct_GK"] >= 50:
        return "GK"
    # goal-threat forwards and attacking mids
    if prof["pct_FWD"] >= 30 or (prof["mean_goals_per_90"] >= 0.25
                                 and prof["mean_threat"] >= 400):
        return "ATT"
    if prof["pct_DEF"] >= 50:
        return "DEF"
    return "MID"


def assign_names(profiles: pd.DataFrame) -> tuple[dict, dict]:
    """Assign distinct role+tier names by ranking archetypes within each role."""
    roles = {int(r.archetype_id): base_role(r) for _, r in profiles.iterrows()}
    idx = profiles.set_index("archetype_id")
    names = {}
    for role in set(roles.values()):
        vocab, metric = ROLE_VOCAB[role]
        ids = sorted((a for a, rr in roles.items() if rr == role),
                     key=lambda a: idx.loc[a, metric], reverse=True)
        for i, a in enumerate(ids):
            names[a] = vocab[i] if i < len(vocab) else f"{vocab[-1]} {i + 1}"
    return names, roles


def profile_group(g: pd.DataFrame) -> dict:
    pos = g["position"].value_counts(normalize=True)
    prof = {
        "size": int(len(g)),
        "pct_GK": round(100 * pos.get("GK", 0), 1),
        "pct_DEF": round(100 * pos.get("DEF", 0), 1),
        "pct_MID": round(100 * pos.get("MID", 0), 1),
        "pct_FWD": round(100 * pos.get("FWD", 0), 1),
        "mean_total_points": round(g["total_points"].mean(), 1),
        "mean_minutes": round(g["minutes"].mean(), 0),
        "mean_cost_m": round(g["now_cost_m"].mean(), 1),
    }
    for c in FEATURES:
        prof[f"mean_{c}"] = round(g[c].mean(), 3)
    return prof


def plot(df, season, out_png, name_lookup):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 7.5))
    cmap = plt.get_cmap("tab20")
    for i, a in enumerate(sorted(df["archetype_id"].unique())):
        sub = df[df["archetype_id"] == a]
        if a == -1:
            ax.scatter(sub["viz_x"], sub["viz_y"], s=16, c="lightgray",
                       label="unclassified", alpha=0.6, edgecolors="none")
        else:
            ax.scatter(sub["viz_x"], sub["viz_y"], s=26, color=cmap(i % 20),
                       label=f"{a}: {name_lookup[a]} (n={len(sub)})", alpha=0.85,
                       edgecolors="none")
    ax.set_title(f"Canonical archetypes — {season}")
    ax.set_xlabel("UMAP-1"); ax.set_ylabel("UMAP-2")
    ax.legend(loc="best", fontsize=6.5, framealpha=0.6, ncol=1)
    fig.tight_layout(); fig.savefig(out_png, dpi=130); plt.close(fig)


def main() -> None:
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import AgglomerativeClustering

    paths = exp.exp_paths(__file__)
    manifest = exp.load_manifest(paths["dir"])
    figdir = paths["outputs"] / "figures"; figdir.mkdir(exist_ok=True)

    panel = pd.read_csv(ALL_PANEL)

    # --- stage 1: per-season fine clustering ----------------------------- #
    per_season = {}   # season -> df with local_cluster, viz coords
    centroids = []    # list of dicts: season, local_cluster, centroid vector, meta
    for season in SEASONS:
        sdf = panel[(panel["season"] == season) &
                    (panel["minutes"] >= MIN_MINUTES)].reset_index(drop=True)
        X = sdf[FEATURES].apply(pd.to_numeric, errors="coerce").fillna(0.0)
        labels, viz = cluster_season(X)
        sdf = sdf.assign(local_cluster=labels, viz_x=viz[:, 0], viz_y=viz[:, 1])
        per_season[season] = (sdf, X)
        for cl in sorted(l for l in set(labels) if l != -1):
            mask = labels == cl
            centroids.append({
                "season": season, "local_cluster": int(cl),
                "vec": X.values[mask].mean(axis=0), "size": int(mask.sum()),
            })

    # --- stage 2: align via meta-clustering of centroids ----------------- #
    C = np.vstack([c["vec"] for c in centroids])
    Cs = StandardScaler().fit_transform(C)
    n_meta = min(N_ARCHETYPES, len(centroids))
    meta = AgglomerativeClustering(n_clusters=n_meta).fit_predict(Cs)
    for c, m in zip(centroids, meta):
        c["archetype_id"] = int(m)
    keymap = {(c["season"], c["local_cluster"]): c["archetype_id"] for c in centroids}

    # --- stage 3: label every player ------------------------------------- #
    labeled = []
    for season in SEASONS:
        sdf, _ = per_season[season]
        sdf = sdf.copy()
        sdf["archetype_id"] = [keymap.get((season, int(lc)), -1) for lc in sdf["local_cluster"]]
        labeled.append(sdf)
    assign = pd.concat(labeled, ignore_index=True)

    # --- stage 4: profile + name canonical archetypes -------------------- #
    prof_rows = []
    for a in sorted(x for x in assign["archetype_id"].unique() if x != -1):
        g = assign[assign["archetype_id"] == a]
        prof = profile_group(g)
        prof["archetype_id"] = int(a)
        prof["seasons_present"] = int(g["season"].nunique())
        prof_rows.append(prof)
    profiles = pd.DataFrame(prof_rows)

    name_lookup, role_lookup = assign_names(profiles)
    profiles["role"] = profiles["archetype_id"].map(role_lookup)
    profiles["name"] = profiles["archetype_id"].map(name_lookup)
    assign["archetype_name"] = assign["archetype_id"].map(
        lambda a: name_lookup.get(a, "Unclassified"))

    # --- outputs --------------------------------------------------------- #
    keep = (["season", "code", "web_name", "position", "team_name"] + CONTEXT +
            ["archetype_id", "archetype_name", "local_cluster", "viz_x", "viz_y"] + FEATURES)
    assign_out = assign[keep].sort_values(["season", "archetype_id", "code"])
    assign_out.to_csv(paths["outputs"] / "player_archetypes.csv", index=False)
    profiles.sort_values("archetype_id").to_csv(
        paths["outputs"] / "archetype_profiles.csv", index=False)
    smap = pd.DataFrame(centroids)[["season", "local_cluster", "archetype_id", "size"]]
    smap["archetype_name"] = smap["archetype_id"].map(name_lookup)
    smap.sort_values(["season", "local_cluster"]).to_csv(
        paths["outputs"] / "season_cluster_map.csv", index=False)
    for season in SEASONS:
        plot(assign[assign["season"] == season], season,
             figdir / f"archetypes_{season}.png", name_lookup)

    # --- validation ------------------------------------------------------ #
    val = {
        "min_minutes": MIN_MINUTES, "n_archetypes_requested": N_ARCHETYPES,
        "n_archetypes_found": int(profiles.shape[0]), "seed": SEED,
        "all_panel_sha256": exp.sha256_file(ALL_PANEL),
        "n_labeled_player_seasons": int(len(assign)),
        "n_unclassified": int((assign["archetype_id"] == -1).sum()),
        "per_season_qualifying": {s: int((assign["season"] == s).sum()) for s in SEASONS},
        "archetypes_present_all_seasons": None,
        "names": {int(r.archetype_id): r["name"] for _, r in profiles.iterrows()},
    }
    # every canonical archetype should appear in all 3 seasons (good alignment)
    present = assign[assign.archetype_id != -1].groupby("archetype_id")["season"].nunique()
    val["archetypes_present_all_seasons"] = int((present == 3).sum())
    val["archetypes_in_1_or_2_seasons"] = int((present < 3).sum())
    (paths["validation"] / "validation.json").write_text(json.dumps(val, indent=2), encoding="utf-8")

    manifest["outputs"] = ["player_archetypes.csv", "archetype_profiles.csv",
                           "season_cluster_map.csv"] + \
                          [f"figures/{p.name}" for p in sorted(figdir.glob('*.png'))]
    manifest["environment"] = exp.capture_environment()
    manifest["git_commit"] = exp.git_commit_hash()
    manifest["all_players_panel_sha256"] = val["all_panel_sha256"]
    exp.save_manifest(paths["dir"], manifest)

    print(f"Canonical archetypes found: {val['n_archetypes_found']} "
          f"(present in all 3 seasons: {val['archetypes_present_all_seasons']})")
    print(f"Labeled player-seasons: {val['n_labeled_player_seasons']} "
          f"(unclassified: {val['n_unclassified']})")
    for _, r in profiles.sort_values("archetype_id").iterrows():
        print(f"  A{int(r.archetype_id)}: {r['name']:42s} n={int(r['size']):3d} "
              f"GK{r.pct_GK:3.0f} DEF{r.pct_DEF:3.0f} MID{r.pct_MID:3.0f} FWD{r.pct_FWD:3.0f}")


if __name__ == "__main__":
    main()
