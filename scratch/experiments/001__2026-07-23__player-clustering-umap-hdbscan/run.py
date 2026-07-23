"""Experiment 001 (player-clustering-umap-hdbscan).

Unsupervised player archetypes from season-aggregate stats, per season, at two
nested granularities (coarse / fine).

Approach
--------
Per season, on players with comparable playing time (>= MIN_MINUTES):
  standardize production/rate features
  -> UMAP (moderate-D) embedding for clustering
  -> HDBSCAN (leaf)        => FINE archetypes (~7-12)
  -> agglomerate the fine-cluster centroids into K_COARSE groups
                            => COARSE archetypes (nested: each fine ⊂ one coarse)
  -> separate 2-D UMAP embedding purely for visualization.

Why nested (not two independent HDBSCAN runs): a second HDBSCAN tuned "coarse"
was unstable across seasons (one season collapsed to 2 clusters while others
gave 6-7). Deriving coarse by merging fine-cluster centroids is stable, keeps
goalkeepers as their own group, and yields a clean hierarchy (fine ⊂ coarse)
that later experiments can build on.

Run from the repository root:
    python scratch/experiments/001__2026-07-23__player-clustering-umap-hdbscan/run.py
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

# Only cluster players with comparable, substantial playing time (~10+ matches)
# so structure reflects style/production, not availability, and per-90 rates are
# reliable. (Chosen after inspecting the minutes distribution; see README.)
MIN_MINUTES = 900

# Number of coarse archetypes (nested groups of the fine clusters).
K_COARSE = 5

# Production + rate profile features. Excludes minutes/starts on purpose.
FEATURES = [
    "goals_scored", "assists", "expected_goals", "expected_assists",
    "expected_goal_involvements",
    "clean_sheets", "goals_conceded", "expected_goals_conceded", "saves",
    "bonus", "bps", "yellow_cards", "red_cards",
    "influence", "creativity", "threat", "ict_index",
    "points_per_90", "goals_per_90", "assists_per_90",
    "xg_per_90", "xa_per_90", "xgi_per_90",
]
CONTEXT_COLS = ["total_points", "now_cost_m", "selected_by_percent", "minutes"]

UMAP_CLUSTER = {"n_neighbors": 12, "min_dist": 0.0, "n_components": 10}
UMAP_VIZ = {"n_neighbors": 15, "min_dist": 0.10, "n_components": 2}
HDBSCAN_FINE = {"min_cluster_size": 15, "min_samples": 3,
                "cluster_selection_method": "leaf"}


def build_feature_matrix(season_df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    X = season_df[FEATURES].apply(pd.to_numeric, errors="coerce")
    n_filled = int(X.isna().sum().sum())
    return X.fillna(0.0), n_filled


def derive_coarse(Xs: np.ndarray, fine: np.ndarray, k: int) -> np.ndarray:
    """Merge fine clusters into k coarse groups by agglomerating their centroids
    (in standardized feature space). Noise (-1) stays noise."""
    from sklearn.cluster import AgglomerativeClustering
    fine_labels = sorted(l for l in set(fine) if l != -1)
    if len(fine_labels) <= k:
        mapping = {f: i for i, f in enumerate(fine_labels)}
    else:
        cents = np.vstack([Xs[fine == f].mean(axis=0) for f in fine_labels])
        merged = AgglomerativeClustering(n_clusters=k).fit_predict(cents)
        mapping = {f: int(c) for f, c in zip(fine_labels, merged)}
    return np.array([mapping.get(f, -1) for f in fine])


def fit_clustering(X: pd.DataFrame):
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import HDBSCAN
    import umap

    Xs = StandardScaler().fit_transform(X.values)
    cluster_emb = umap.UMAP(random_state=SEED, metric="euclidean",
                            **UMAP_CLUSTER).fit_transform(Xs)
    fine = HDBSCAN(**HDBSCAN_FINE).fit_predict(cluster_emb)
    coarse = derive_coarse(Xs, fine, K_COARSE)
    viz_emb = umap.UMAP(random_state=SEED, metric="euclidean",
                        **UMAP_VIZ).fit_transform(Xs)
    return cluster_emb, viz_emb, fine, coarse


def cluster_profiles(df: pd.DataFrame, season: str, level: str,
                     label_col: str) -> pd.DataFrame:
    rows = []
    for cl, g in df.groupby(label_col):
        pos = g["position"].value_counts(normalize=True)
        exemplars = ", ".join(
            g.sort_values("total_points", ascending=False)["web_name"].head(5))
        row = {
            "season": season, "level": level, "cluster": int(cl),
            "label": "noise" if cl == -1 else f"{level[0]}{cl}",
            "size": int(len(g)),
            "pct_GK": round(100 * pos.get("GK", 0), 1),
            "pct_DEF": round(100 * pos.get("DEF", 0), 1),
            "pct_MID": round(100 * pos.get("MID", 0), 1),
            "pct_FWD": round(100 * pos.get("FWD", 0), 1),
            "mean_total_points": round(g["total_points"].mean(), 1),
            "mean_minutes": round(g["minutes"].mean(), 0),
            "mean_cost_m": round(g["now_cost_m"].mean(), 1),
            "exemplars": exemplars,
        }
        for f in FEATURES:
            row[f"mean_{f}"] = round(g[f].mean(), 3)
        rows.append(row)
    return pd.DataFrame(rows).sort_values("cluster").reset_index(drop=True)


def plot_embedding(df, season, level, label_col, out_png):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 7))
    cmap = plt.get_cmap("tab10" if level == "coarse" else "tab20")
    for i, cl in enumerate(sorted(df[label_col].unique())):
        sub = df[df[label_col] == cl]
        if cl == -1:
            ax.scatter(sub["viz_x"], sub["viz_y"], s=18, c="lightgray",
                       label="noise", alpha=0.6, edgecolors="none")
        else:
            ax.scatter(sub["viz_x"], sub["viz_y"], s=28, color=cmap(i % cmap.N),
                       label=f"{level[0]}{cl} (n={len(sub)})", alpha=0.85,
                       edgecolors="none")
    ax.set_title(f"UMAP + HDBSCAN — {season} ({level}, min_minutes={MIN_MINUTES})")
    ax.set_xlabel("UMAP-1"); ax.set_ylabel("UMAP-2")
    ax.legend(loc="best", fontsize=7, framealpha=0.6, ncol=2)
    fig.tight_layout(); fig.savefig(out_png, dpi=130); plt.close(fig)


def main() -> None:
    paths = exp.exp_paths(__file__)
    manifest = exp.load_manifest(paths["dir"])
    figdir = paths["outputs"] / "figures"
    figdir.mkdir(exist_ok=True)

    core = exp.load_core(verify=manifest.get("core_dataset_fingerprint") or None)
    panel = core["season_panel"]

    from sklearn.metrics import silhouette_score

    all_assign, all_profiles = [], []
    val = {"min_minutes": MIN_MINUTES, "k_coarse": K_COARSE, "seed": SEED,
           "features": FEATURES, "umap_cluster": UMAP_CLUSTER,
           "hdbscan_fine": HDBSCAN_FINE, "seasons": {}}

    for season in SEASONS:
        full = panel[panel["season"] == season]
        sdf = full[full["minutes"] >= MIN_MINUTES].reset_index(drop=True)
        X, n_filled = build_feature_matrix(sdf)
        cluster_emb, viz_emb, fine, coarse = fit_clustering(X)

        out = sdf[["code", "web_name", "position", "team_name"] +
                  CONTEXT_COLS + FEATURES].copy()
        out.insert(0, "season", season)
        out["coarse_cluster"] = coarse
        out["fine_cluster"] = fine
        out["viz_x"], out["viz_y"] = viz_emb[:, 0], viz_emb[:, 1]
        all_assign.append(out)

        season_val = {"n_all_players": int(len(full)),
                      "n_clustered": int(len(sdf)),
                      "n_excluded_below_min": int((full["minutes"] < MIN_MINUTES).sum()),
                      "n_nan_features_filled": n_filled, "levels": {}}
        for level, labels, col in [("coarse", coarse, "coarse_cluster"),
                                    ("fine", fine, "fine_cluster")]:
            all_profiles.append(cluster_profiles(out, season, level, col))
            n_noise = int((labels == -1).sum())
            n_clusters = len({l for l in labels if l != -1})
            mask = labels != -1
            sil = (round(float(silhouette_score(cluster_emb[mask], labels[mask])), 3)
                   if n_clusters >= 2 and mask.sum() > n_clusters else None)
            season_val["levels"][level] = {
                "n_clusters": n_clusters, "n_noise": n_noise,
                "noise_fraction": round(n_noise / len(labels), 3),
                "silhouette": sil}
            plot_embedding(out, season, level, col,
                           figdir / f"umap_{season}_{level}.png")
        val["seasons"][season] = season_val

    assign_df = pd.concat(all_assign, ignore_index=True)
    profiles_df = pd.concat(all_profiles, ignore_index=True)
    assign_path = paths["outputs"] / "player_clusters.csv"
    profiles_path = paths["outputs"] / "cluster_profiles.csv"
    assign_df.to_csv(assign_path, index=False, encoding="utf-8")
    profiles_df.to_csv(profiles_path, index=False, encoding="utf-8")

    # -- validation checkpoint -------------------------------------------- #
    val["assignment_rows"] = int(len(assign_df))
    val["expected_rows"] = sum(v["n_clustered"] for v in val["seasons"].values())
    val["rows_match"] = val["assignment_rows"] == val["expected_rows"]
    val["no_nan_in_clustered_features"] = bool(assign_df[FEATURES].notna().all().all())
    val["coarse_is_nested_in_fine"] = bool(
        (assign_df.groupby(["season", "fine_cluster"])["coarse_cluster"]
         .nunique() == 1).all())
    (paths["validation"] / "clustering_validation.json").write_text(
        json.dumps(val, indent=2), encoding="utf-8")

    vlines = ["# Clustering validation", "",
              f"- Seed: {SEED} · min_minutes: {MIN_MINUTES} · K_coarse: {K_COARSE}",
              f"- Features ({len(FEATURES)}): {', '.join(FEATURES)}",
              f"- Assignment rows: {val['assignment_rows']} "
              f"(expected {val['expected_rows']}, match: {val['rows_match']})",
              f"- Coarse nested in fine: {val['coarse_is_nested_in_fine']}",
              f"- No NaN in clustered features: {val['no_nan_in_clustered_features']}", "",
              "| Season | Clustered | Excluded(<min) | Level | Clusters | Noise | Silhouette |",
              "|---|---|---|---|---|---|---|"]
    for s in SEASONS:
        sv = val["seasons"][s]
        for level in ("coarse", "fine"):
            lv = sv["levels"][level]
            vlines.append(f"| {s} | {sv['n_clustered']} | {sv['n_excluded_below_min']} | "
                          f"{level} | {lv['n_clusters']} | {lv['n_noise']} | {lv['silhouette']} |")
    (paths["validation"] / "clustering_validation.md").write_text(
        "\n".join(vlines), encoding="utf-8")

    written = ["player_clusters.csv", "cluster_profiles.csv"] + \
              [f"figures/{p.name}" for p in sorted(figdir.glob("*.png"))]
    manifest["outputs"] = written
    manifest["environment"] = exp.capture_environment()
    manifest["git_commit"] = exp.git_commit_hash()
    exp.save_manifest(paths["dir"], manifest)

    print("Done.")
    for s in SEASONS:
        sv = val["seasons"][s]
        c, f = sv["levels"]["coarse"], sv["levels"]["fine"]
        print(f"  {s}: {sv['n_clustered']} players | coarse={c['n_clusters']} "
              f"(sil {c['silhouette']}) | fine={f['n_clusters']} "
              f"(sil {f['silhouette']}, noise {f['n_noise']})")


if __name__ == "__main__":
    main()
