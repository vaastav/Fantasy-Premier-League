"""Scaffold a new isolated experiment folder.

Usage (from repo root):
    python scratch/experiments/new_experiment.py <slug> [--title "Human title"] \
        [--author NAME] [--rationale "one line"] [--depends-on 001 004]

Creates scratch/experiments/NNN__YYYY-MM-DD__slug/ from the template, pins the
current core-dataset fingerprint into its manifest, and regenerates the ledger.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import experiment as exp  # noqa: E402

TEMPLATE = exp.EXPERIMENTS / "_template"
FOLDER_RE = re.compile(r"^(\d{3})__\d{4}-\d{2}-\d{2}__")


def next_id() -> str:
    ids = []
    for p in exp.EXPERIMENTS.iterdir():
        if p.is_dir():
            m = FOLDER_RE.match(p.name)
            if m:
                ids.append(int(m.group(1)))
    return f"{(max(ids) + 1) if ids else 1:03d}"


def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "experiment"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", help="short kebab-case name, e.g. price-vs-points")
    ap.add_argument("--title", default="")
    ap.add_argument("--author", default="")
    ap.add_argument("--rationale", default="")
    ap.add_argument("--depends-on", nargs="*", default=[])
    args = ap.parse_args()

    slug = slugify(args.slug)
    exp_id = next_id()
    date = dt.date.today().isoformat()
    folder = f"{exp_id}__{date}__{slug}"
    dest = exp.EXPERIMENTS / folder
    if dest.exists():
        raise SystemExit(f"Refusing to overwrite existing {dest}")

    shutil.copytree(TEMPLATE, dest)
    (dest / "outputs").mkdir(exist_ok=True)
    (dest / "validation").mkdir(exist_ok=True)
    (dest / "outputs" / ".gitkeep").touch()
    (dest / "validation" / ".gitkeep").touch()

    # Fill placeholders in text files.
    repl = {"__ID__": exp_id, "__SLUG__": slug, "__DATE__": date, "__FOLDER__": folder}
    for fname in ("README.md", "run.py"):
        p = dest / fname
        text = p.read_text(encoding="utf-8")
        for k, v in repl.items():
            text = text.replace(k, v)
        p.write_text(text, encoding="utf-8")

    # Fill + pin the manifest.
    manifest = json.loads((dest / "manifest.json").read_text(encoding="utf-8"))
    manifest.update({
        "id": exp_id,
        "slug": slug,
        "title": args.title,
        "date_created": date,
        "author": args.author,
        "rationale": args.rationale,
        "depends_on": list(args.depends_on),
        "core_dataset_fingerprint": exp.core_fingerprint(),
    })
    manifest["inputs"]["upstream_experiments"] = list(args.depends_on)
    exp.save_manifest(dest, manifest)

    # Regenerate the ledger.
    import ledger
    ledger.build()

    print(f"Created {dest.relative_to(exp.REPO_ROOT)}")
    print("Core dataset pinned. Next:")
    print(f"  1. edit {folder}/README.md (question, rationale, method)")
    print(f"  2. implement {folder}/run.py")
    print(f"  3. python scratch/experiments/{folder}/run.py")
    print(f"  4. set status=complete + key_findings in manifest, rerun ledger.py")
    print(f"  5. git add + commit  'exp({exp_id}): <summary>'  + push")


if __name__ == "__main__":
    main()
