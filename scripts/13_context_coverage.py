"""Coverage straight from the context files, before any answers exist.

Coverage = share of entity questions (with an Arabic gold label) whose
normalised gold label appears in the context lines. The same definition as
scripts/07 and scripts/12, which read it back from the answer files.

Run: py -3.14 scripts/13_context_coverage.py [--scale 4000]
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.qa.mintaka_loader import load_split, select_scale  # noqa: E402
from src.qa.qa_scorer import normalize_arabic  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", default="4000")
    args = ap.parse_args()
    qs = select_scale(load_split(ROOT / "datasets" / "mintaka" / "mintaka_test.json"), args.scale)
    ent = [q for q in qs if q.answer_type == "entity" and any(q.answer_labels_ar)]
    print(f"scale {args.scale}: {len(ent)} entity questions with an Arabic gold label")
    for path in sorted((ROOT / "results" / "contexts" / str(args.scale)).glob("*.jsonl")):
        if "limit" in path.name:
            continue
        ctx = {r["item_id"]: r["lines"] for r in map(json.loads, open(path, encoding="utf-8"))}
        hit = 0
        for q in ent:
            text = normalize_arabic("\n".join(ctx.get(q.id, [])))
            hit += any(l and normalize_arabic(l) in text for l in q.answer_labels_ar if l)
        lens = sorted(len(v) for v in ctx.values())
        print(f"   {path.stem:<22} coverage {100 * hit / len(ent):5.1f}%  ({hit}/{len(ent)})   "
              f"lines: median {lens[len(lens) // 2]}, mean {sum(lens) / len(lens):.1f}")


if __name__ == "__main__":
    main()
