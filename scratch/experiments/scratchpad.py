"""Scratch working file for exploratory FPL analytics.

This is a safe sandbox for quick, agent-assisted exploration. Follow the rules
in `scratch/AGENTIC_ANALYTICS_GUIDE.md` and `scratch/DATA_SAFETY_CHECKLIST.md`:

- Treat everything under `data/` as read-only source data.
- Write any derived output under `scratch/summaries/`, `scratch/validation/`,
  or `scratch/visuals/` using new, descriptively named files.
- Use repository-relative paths only.

Run from the repository root, e.g.:  python scratch/experiments/scratchpad.py
"""

from pathlib import Path

# Repo-relative anchors (this file lives at scratch/experiments/scratchpad.py).
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"            # read-only source data
SUMMARIES_DIR = REPO_ROOT / "scratch" / "summaries"
VALIDATION_DIR = REPO_ROOT / "scratch" / "validation"
VISUALS_DIR = REPO_ROOT / "scratch" / "visuals"


def main() -> None:
    print(f"Repo root:   {REPO_ROOT}")
    print(f"Data dir:    {DATA_DIR} (read-only)")
    print(f"Summaries:   {SUMMARIES_DIR}")
    print(f"Validation:  {VALIDATION_DIR}")
    print(f"Visuals:     {VISUALS_DIR}")
    # Start experimenting below.


if __name__ == "__main__":
    main()
