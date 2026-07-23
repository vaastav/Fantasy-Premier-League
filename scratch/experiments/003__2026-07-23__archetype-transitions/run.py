"""Experiment 003 (archetype-transitions).

Which players change archetype from one season to the next, and what are the
common role transitions? Consumes exp 002's labeled player-archetypes.

A transition exists for a player who is classified (>=900 min, not noise) in
BOTH seasons of a consecutive pair (2023-24->2024-25, 2024-25->2025-26).

Outputs:
- outputs/transitions_long.csv         one row per player per season-pair
- outputs/transition_matrix_<pair>.csv from-archetype x to-archetype counts
- outputs/transition_summary.csv       per-pair: stayed / changed counts
- outputs/figures/                      transition heatmaps

Run: python scratch/experiments/003__2026-07-23__archetype-transitions/run.py
"""
from __future__ import annotations
import json, sys, pathlib
import numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from _lib import experiment as exp  # noqa: E402

SEASONS = ["2023-24", "2024-25", "2025-26"]
PAIRS = [("2023-24", "2024-25"), ("2024-25", "2025-26")]


def heatmap(mat: pd.DataFrame, title: str, out_png: pathlib.Path):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(mat.values, cmap="Blues")
    ax.set_xticks(range(len(mat.columns))); ax.set_xticklabels(mat.columns, rotation=45, ha="right", fontsize=7)
    ax.set_yticks(range(len(mat.index))); ax.set_yticklabels(mat.index, fontsize=7)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat.values[i, j]
            if v: ax.text(j, i, int(v), ha="center", va="center", fontsize=7,
                          color="white" if v > mat.values.max() * 0.5 else "black")
    ax.set_xlabel("to archetype"); ax.set_ylabel("from archetype")
    ax.set_title(title); fig.colorbar(im, fraction=0.046)
    fig.tight_layout(); fig.savefig(out_png, dpi=130); plt.close(fig)


def main() -> None:
    paths = exp.exp_paths(__file__)
    manifest = exp.load_manifest(paths["dir"])
    figdir = paths["outputs"] / "figures"; figdir.mkdir(exist_ok=True)

    lab = exp.load_experiment_output("002", "player_archetypes.csv")
    lab = lab[lab["archetype_name"] != "Unclassified"].copy()

    names = sorted(lab["archetype_name"].unique())
    trans_rows, summary_rows = [], []
    for s0, s1 in PAIRS:
        a = lab[lab.season == s0][["code", "web_name", "archetype_name", "total_points", "now_cost_m"]]
        b = lab[lab.season == s1][["code", "web_name", "archetype_name", "total_points"]]
        m = a.merge(b, on="code", suffixes=("_from", "_to"))
        m["pair"] = f"{s0}->{s1}"
        m["changed"] = m["archetype_name_from"] != m["archetype_name_to"]
        trans_rows.append(m)

        mat = pd.crosstab(m["archetype_name_from"], m["archetype_name_to"]).reindex(
            index=names, columns=names, fill_value=0)
        mat.to_csv(paths["outputs"] / f"transition_matrix_{s0}_to_{s1}.csv")
        heatmap(mat, f"Archetype transitions {s0} -> {s1}",
                figdir / f"transitions_{s0}_to_{s1}.png")

        summary_rows.append({
            "pair": f"{s0}->{s1}", "n_players": int(len(m)),
            "n_stayed": int((~m["changed"]).sum()),
            "n_changed": int(m["changed"].sum()),
            "pct_stayed": round(100 * (~m["changed"]).mean(), 1),
        })

    trans = pd.concat(trans_rows, ignore_index=True)
    trans_out = trans[["pair", "code", "web_name_from", "archetype_name_from",
                       "archetype_name_to", "changed",
                       "total_points_from", "total_points_to"]].rename(
        columns={"web_name_from": "web_name"})
    trans_out.to_csv(paths["outputs"] / "transitions_long.csv", index=False)
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(paths["outputs"] / "transition_summary.csv", index=False)

    # most common CHANGES (excluding stayers)
    changes = (trans[trans.changed]
               .groupby(["archetype_name_from", "archetype_name_to"]).size()
               .reset_index(name="n").sort_values("n", ascending=False))
    changes.to_csv(paths["outputs"] / "top_changes.csv", index=False)

    val = {"pairs": summary_rows,
           "n_transition_rows": int(len(trans)),
           "overall_pct_stayed": round(100 * (~trans["changed"]).mean(), 1),
           "n_distinct_change_types": int(len(changes))}
    (paths["validation"] / "validation.json").write_text(json.dumps(val, indent=2), encoding="utf-8")

    manifest["outputs"] = ["transitions_long.csv", "transition_summary.csv",
                           "top_changes.csv"] + \
        [f"transition_matrix_{a}_to_{b}.csv" for a, b in PAIRS] + \
        [f"figures/{p.name}" for p in sorted(figdir.glob('*.png'))]
    manifest["environment"] = exp.capture_environment()
    manifest["git_commit"] = exp.git_commit_hash()
    exp.save_manifest(paths["dir"], manifest)

    print(f"Transitions: {len(trans)} player-pairs | overall stayed "
          f"{val['overall_pct_stayed']}%")
    for r in summary_rows:
        print(f"  {r['pair']}: {r['n_players']} players, {r['pct_stayed']}% stayed")
    print("Top role changes:")
    for _, r in changes.head(6).iterrows():
        print(f"  {r.archetype_name_from} -> {r.archetype_name_to}: {r.n}")


if __name__ == "__main__":
    main()
