"""Experiment 005 (team-archetype-clustering).

Represent each team-season by the archetype composition of its qualifying
(>=900-min, classified) players, then cluster team-seasons. Consumes exp 002.

Features per team-season: for each of the 9 canonical archetypes, the COUNT of
players and the PROPORTION of the team's classified squad (18 features total).

Clustering: standardize -> HDBSCAN on the standardized feature space (60 team-
seasons is small, so we cluster the features directly and use a 2-D UMAP only
for visualization).

Outputs:
- outputs/team_archetype_features.csv  team-season x (counts + proportions)
- outputs/team_clusters.csv            team-season -> cluster + coords
- outputs/team_cluster_profiles.csv    mean composition per team cluster
- outputs/figures/team_clusters.png

Run: python scratch/experiments/005__2026-07-23__team-archetype-clustering/run.py
"""
from __future__ import annotations
import json, sys, pathlib
import numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _lib import experiment as exp  # noqa: E402

SEED = 42
HDBSCAN_TEAM = {"min_cluster_size": 3, "min_samples": 1,
                "cluster_selection_method": "eom"}


def main() -> None:
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import HDBSCAN
    import umap

    paths = exp.exp_paths(__file__)
    manifest = exp.load_manifest(paths["dir"])
    figdir = paths["outputs"] / "figures"; figdir.mkdir(exist_ok=True)

    lab = exp.load_experiment_output("002", "player_archetypes.csv")
    classified = lab[lab["archetype_name"] != "Unclassified"].copy()
    archetypes = sorted(classified["archetype_name"].unique())

    # counts per (season, team, archetype)
    counts = (classified.groupby(["season", "team_name", "archetype_name"]).size()
              .unstack(fill_value=0).reindex(columns=archetypes, fill_value=0))
    counts.columns = [f"n__{c}" for c in counts.columns]
    counts = counts.reset_index()
    counts["n_classified"] = counts[[c for c in counts.columns if c.startswith("n__")]].sum(axis=1)

    # proportions
    for a in archetypes:
        counts[f"p__{a}"] = counts[f"n__{a}"] / counts["n_classified"]

    feat_cols = [f"n__{a}" for a in archetypes] + [f"p__{a}" for a in archetypes]
    counts.to_csv(paths["outputs"] / "team_archetype_features.csv", index=False)

    # cluster team-seasons. Team compositions form more of a continuum than
    # density-separated clusters, so the PRIMARY partition is agglomerative with
    # K chosen by silhouette; HDBSCAN is kept as a density robustness check.
    from sklearn.cluster import AgglomerativeClustering
    from sklearn.metrics import silhouette_score

    X = StandardScaler().fit_transform(counts[feat_cols].values)
    best_k, best_sil, best_labels = None, -1, None
    for k in range(3, 8):
        lab_k = AgglomerativeClustering(n_clusters=k).fit_predict(X)
        sil = silhouette_score(X, lab_k)
        if sil > best_sil:
            best_k, best_sil, best_labels = k, sil, lab_k
    labels = best_labels
    hdb_labels = HDBSCAN(**HDBSCAN_TEAM).fit_predict(X)

    viz = umap.UMAP(n_neighbors=10, min_dist=0.15, n_components=2,
                    random_state=SEED).fit_transform(X)
    counts["team_cluster"] = labels
    counts["team_cluster_hdbscan"] = hdb_labels
    counts["viz_x"], counts["viz_y"] = viz[:, 0], viz[:, 1]
    print(f"Agglomerative K={best_k} (silhouette {best_sil:.3f}); "
          f"HDBSCAN found {len({l for l in hdb_labels if l!=-1})} clusters "
          f"+ {int((hdb_labels==-1).sum())} noise")

    out_cols = ["season", "team_name", "n_classified", "team_cluster",
                "team_cluster_hdbscan", "viz_x", "viz_y"] + feat_cols
    counts[out_cols].to_csv(paths["outputs"] / "team_clusters.csv", index=False)

    # cluster profiles: mean proportion per archetype + member teams
    prof_rows = []
    for cl, g in counts.groupby("team_cluster"):
        row = {"team_cluster": int(cl), "size": int(len(g)),
               "mean_n_classified": round(g["n_classified"].mean(), 1),
               "members": ", ".join(f"{r.team_name}({r.season[-2:]})"
                                     for _, r in g.iterrows())}
        for a in archetypes:
            row[f"mean_p__{a}"] = round(g[f"p__{a}"].mean(), 3)
        prof_rows.append(row)
    profiles = pd.DataFrame(prof_rows).sort_values("team_cluster")
    profiles.to_csv(paths["outputs"] / "team_cluster_profiles.csv", index=False)

    # figure
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(11, 8))
    cmap = plt.get_cmap("tab10")
    for i, cl in enumerate(sorted(counts["team_cluster"].unique())):
        sub = counts[counts["team_cluster"] == cl]
        c = "lightgray" if cl == -1 else cmap(i % 10)
        ax.scatter(sub["viz_x"], sub["viz_y"], s=60, color=c,
                   label=("noise" if cl == -1 else f"cluster {cl} (n={len(sub)})"),
                   alpha=0.85, edgecolors="k", linewidths=0.3)
        for _, r in sub.iterrows():
            ax.annotate(f"{r.team_name[:3]}{r.season[-2:]}", (r.viz_x, r.viz_y),
                        fontsize=6, alpha=0.8)
    ax.set_title("Team-seasons clustered by archetype makeup")
    ax.set_xlabel("UMAP-1"); ax.set_ylabel("UMAP-2")
    ax.legend(loc="best", fontsize=7)
    fig.tight_layout(); fig.savefig(figdir / "team_clusters.png", dpi=130); plt.close(fig)

    val = {"n_team_seasons": int(len(counts)),
           "n_features": len(feat_cols),
           "primary_method": "agglomerative",
           "primary_k": int(best_k),
           "primary_silhouette": round(float(best_sil), 3),
           "hdbscan_n_clusters": int(len({l for l in hdb_labels if l != -1})),
           "hdbscan_n_noise": int((hdb_labels == -1).sum()),
           "archetypes": archetypes}
    (paths["validation"] / "validation.json").write_text(json.dumps(val, indent=2), encoding="utf-8")

    manifest["outputs"] = ["team_archetype_features.csv", "team_clusters.csv",
                           "team_cluster_profiles.csv", "figures/team_clusters.png"]
    manifest["environment"] = exp.capture_environment()
    manifest["git_commit"] = exp.git_commit_hash()
    exp.save_manifest(paths["dir"], manifest)

    print(f"Team-seasons: {len(counts)} | features: {len(feat_cols)} | "
          f"agglomerative K={val['primary_k']} (sil {val['primary_silhouette']})")
    for _, r in profiles.iterrows():
        if r.team_cluster == -1:
            print(f"  noise (n={r['size']}): {r['members']}")
        else:
            top = sorted(((a, r[f'mean_p__{a}']) for a in archetypes),
                         key=lambda x: -x[1])[:3]
            tops = ", ".join(f"{a.split(' ')[0]} {p:.0%}" for a, p in top)
            print(f"  cluster {int(r.team_cluster)} (n={r['size']}): top[{tops}] | {r['members'][:80]}")


if __name__ == "__main__":
    main()
