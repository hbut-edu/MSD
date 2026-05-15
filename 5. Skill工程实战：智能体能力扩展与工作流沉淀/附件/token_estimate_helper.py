#!/usr/bin/env python3
"""Rough token estimator for classroom A/B comparisons.

This script is intentionally simple. It does not replace provider-side token
accounting, but it helps students compare two runs with the same approximation.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def estimate_tokens(text: str) -> int:
    """Estimate tokens with a mixed Chinese/English heuristic."""
    cjk_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    latin_words = len(re.findall(r"[A-Za-z0-9_]+(?:[-'][A-Za-z0-9_]+)*", text))
    other_chars = len(re.findall(r"[^\sA-Za-z0-9_\u4e00-\u9fff]", text))

    # This heuristic is only for relative comparison in this course lab.
    return round(cjk_chars / 1.5 + latin_words / 0.75 + other_chars / 4)


def summarize_file(path: Path) -> dict[str, object]:
    """Return basic character and estimated token statistics for one file."""
    text = path.read_text(encoding="utf-8")
    return {
        "file": str(path),
        "characters": len(text),
        "estimated_tokens": estimate_tokens(text),
    }


def main() -> None:
    """Print JSON statistics for one or more text files."""
    parser = argparse.ArgumentParser(
        description="Estimate tokens for classroom Skill A/B comparisons."
    )
    parser.add_argument("files", nargs="+", type=Path, help="Text files to estimate")
    args = parser.parse_args()

    results = [summarize_file(path) for path in args.files]
    total = sum(item["estimated_tokens"] for item in results)
    print(json.dumps({"files": results, "total_estimated_tokens": total}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
