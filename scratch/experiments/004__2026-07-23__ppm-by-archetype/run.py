"""Experiment 004 (ppm-by-archetype).

Which archetypes deliver the best FPL value — points per million (PPM)?
Consumes exp 002's labeled player-archetypes. PPM = total_points / now_cost_m
(end-of-season price). Classified players only.

Outputs:
- outputs/ppm_by_archetype.csv         pooled PPM stats per archetype
- outputs/ppm_by_archetype_season.csv  PPM per archetype per season
- outputs/figures/ppm_by_archetype.png boxplot (sorted by median PPM)

Run: python scratch/experiments/004__2026-07-23__ppm-by-archetype/run.py
"""
from __future__ import annotations
import json, sys, pathlib
import numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _lib import experiment as exp  # noqa: E402

SEASONS = ["2023-24", "2024-25", "2025-26"]


def main() -> None:
    paths = exp.exp_paths(__file__)
    manifest = exp.load_manifest(paths["dir"])
    figdir = paths["outputs"] / "figures"; figdir.mkdir(exist_ok=True)

    lab = exp.load_experiment_output("002", "player_archetypes.csv")
    lab = lab[(lab["archetype_name"] != "Unclassified") & (lab["now_cost_m"] > 0)].copy()
    lab["ppm"] = lab["total_points"] / lab["now_cost_m"]

    def stats(g):
        return pd.Series({
            "n": len(g),
            "mean_ppm": round(g["ppm"].mean(), 2),
            "median_ppm": round(g["ppm"].median(), 2),
            "p25_ppm": round(g["ppm"].quantile(0.25), 2),
            "p75_ppm": round(g["ppm"].quantile(0.75), 2),
            "mean_points": round(g["total_points"].mean(), 1),
            "mean_cost_m": round(g["now_cost_m"].mean(), 1),
        })

    by_arch = lab.groupby("archetype_name").apply(stats, include_groups=False)\
                 .reset_index().sort_values("median_ppm", ascending=False)
    by_arch.to_csv(paths["outputs"] / "ppm_by_archetype.csv", index=False)

    by_as = lab.groupby(["archetype_name", "season"]).apply(stats, include_groups=False)\
               .reset_index()
    by_as.to_csv(paths["outputs"] / "ppm_by_archetype_season.csv", index=False)

    # boxplot ordered by median PPM
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    order = by_arch["archetype_name"].tolist()
    data = [lab[lab.archetype_name == a]["ppm"].values for a in order]
    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.boxplot(data, vert=False, tick_labels=order, showfliers=False)
    medians = [np.median(d) for d in data]
    for i, mdn in enumerate(medians):
        ax.text(mdn, i + 1, f" {mdn:.1f}", va="center", fontsize=8)
    ax.set_xlabel("Points per £m (end-of-season price)")
    ax.set_title("FPL value by archetype (all seasons pooled)")
    ax.invert_yaxis(); fig.tight_layout()
    fig.savefig(figdir / "ppm_by_archetype.png", dpi=130); plt.close(fig)

    val = {"n_players": int(len(lab)),
           "overall_median_ppm": round(float(lab["ppm"].median()), 2),
           "best_value_archetype": by_arch.iloc[0]["archetype_name"],
           "best_value_median_ppm": float(by_arch.iloc[0]["median_ppm"]),
           "worst_value_archetype": by_arch.iloc[-1]["archetype_name"]}
    (paths["validation"] / "validation.json").write_text(json.dumps(val, indent=2), encoding="utf-8")

    manifest["outputs"] = ["ppm_by_archetype.csv", "ppm_by_archetype_season.csv",
                           "figures/ppm_by_archetype.png"]
    manifest["environment"] = exp.capture_environment()
    manifest["git_commit"] = exp.git_commit_hash()
    exp.save_manifest(paths["dir"], manifest)

    print(f"PPM by archetype (median, pooled) — overall median {val['overall_median_ppm']}:")
    for _, r in by_arch.iterrows():
        print(f"  {r['archetype_name']:35s} median {r['median_ppm']:5.1f} "
              f"(n={int(r['n']):3d}, pts {r['mean_points']:.0f}, £{r['mean_cost_m']:.1f}m)")


if __name__ == "__main__":
    main()
