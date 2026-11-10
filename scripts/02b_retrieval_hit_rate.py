"""Retrieval hit rate per embedding model, from the files scripts/02
already wrote. No model call and no LLM call: this number decides which
two of the seven embedding models go through answer generation, and it is
available before any answer is generated.

Kept separate from scripts/02 rather than folded into it so the metric can
be recomputed over existing runs without re-embedding an 85,000-sentence
corpus seven times.

Usage:
    python scripts/02b_retrieval_hit_rate.py --scale 100 --split test
"""

import argparse
import json
import logging
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASETS_ROOT = ROOT / "datasets" / "mintaka"
sys.path.insert(0, str(ROOT))

from src.qa.mintaka_loader import load_split, select_scale  # noqa: E402
from src.qa.retrieval import retrieval_hit  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

SPLIT_FILES = {"train": "mintaka_train.json", "dev": "mintaka_dev.json", "test": "mintaka_test.json"}
RETRIEVAL_DIR = ROOT / "results" / "retrieval"
TABLES_DIR = ROOT / "results" / "tables"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scale", required=True)
    parser.add_argument("--split", default="test", choices=["train", "dev", "test"])
    args = parser.parse_args()

    questions = {q.id: q for q in select_scale(load_split(DATASETS_ROOT / SPLIT_FILES[args.split]), args.scale)}
    files = sorted((RETRIEVAL_DIR / str(args.scale)).glob(f"*_{args.scale}.jsonl"))
    if not files:
        raise SystemExit(f"no retrieval output for scale {args.scale} in {RETRIEVAL_DIR}")

    summary = {}
    for path in files:
        model = path.name[: -len(f"_{args.scale}.jsonl")]
        hits, scored, errors = 0, 0, 0
        by_type: dict[str, list[int]] = defaultdict(list)
        by_category: dict[str, list[int]] = defaultdict(list)

        with open(path, encoding="utf-8") as f:
            for line in f:
                row = json.loads(line)
                q = questions.get(row["item_id"])
                if q is None:
                    continue
                # A failed item is written by run_job as {"error": ...} with no
                # "retrieved" key. Counting it as a miss would charge a model
                # for an Ollama timeout.
                if "error" in row:
                    errors += 1
                    continue
                hit = retrieval_hit(row.get("retrieved", []), q.answer_type, q.answer_qids, q.answer_text)
                if hit is None:  # boolean answers, and anything with no gold value to find
                    continue
                scored += 1
                hits += hit
                by_type[q.complexity_type].append(int(hit))
                by_category[q.category].append(int(hit))

        if errors:
            logger.warning("%s: %d rows recorded an error and were excluded, not counted as misses", model, errors)
        summary[model] = {
            "hit_rate": hits / scored if scored else 0.0,
            "hits": hits,
            "n_scored": scored,
            "n_errors": errors,
            "n_skipped": len(questions) - scored - errors,
            "by_complexity_type": {k: {"hit_rate": sum(v) / len(v), "n": len(v)} for k, v in sorted(by_type.items())},
            "by_category": {k: {"hit_rate": sum(v) / len(v), "n": len(v)} for k, v in sorted(by_category.items())},
        }
        logger.info("%-58s hit rate %.3f (%d/%d)", model, summary[model]["hit_rate"], hits, scored)

    out_dir = TABLES_DIR / str(args.scale)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"retrieval_hit_rate_{args.scale}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"scale": args.scale, "split": args.split, "models": summary}, f, ensure_ascii=False, indent=1)
    logger.info("wrote %s", out_path)

    ranked = sorted(summary.items(), key=lambda kv: -kv[1]["hit_rate"])
    print(f"\n{'embedding model':<58}{'hit rate':>10}{'hits/scored':>14}")
    for model, s in ranked:
        print(f"{model:<58}{s['hit_rate']:>9.3f}{s['hits']:>8}/{s['n_scored']:<5}")
    if len(ranked) >= 2:
        print(f"\ntop two by hit rate: {ranked[0][0]}, {ranked[1][0]}")


if __name__ == "__main__":
    main()
