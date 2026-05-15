"""Validate story documentation inventory against plan file."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

DEFAULT_PLAN_NAME = "cofepris-brsdm-scraper-plan_a6b8f794.plan.md"
PLAN_PATH = Path(
    os.getenv(
        "COFEPRIS_PLAN_PATH",
        f"/Users/AndresGonzalez/.cursor/plans/{DEFAULT_PLAN_NAME}",
    )
)
STORIES_ROOT = Path("docs/stories")

HU_PATTERN = re.compile(r"\*\*HU-(\d+\.\d+)\*\*")


def main() -> int:
    if not PLAN_PATH.exists():
        print(f"Plan file not found: {PLAN_PATH}")
        return 1

    plan_content = PLAN_PATH.read_text(encoding="utf-8")
    required_hus = set(HU_PATTERN.findall(plan_content))
    if not required_hus:
        print("No HU entries found in plan.")
        return 1

    existing_hus: set[str] = set()
    for file_path in STORIES_ROOT.rglob("HU-*.md"):
        match = re.search(r"HU-(\d+\.\d+)", file_path.name)
        if match:
            existing_hus.add(match.group(1))

    missing = sorted(required_hus - existing_hus, key=lambda x: tuple(map(int, x.split("."))))
    if missing:
        print("Missing story docs:")
        for hu in missing:
            print(f"- HU-{hu}")
        return 1

    print("Story docs validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
