"""Scores every results/answers/*.jsonl file for one scale tier against
Mintaka's gold answer, using src/qa/qa_scorer.py's per-answer-type matching
and complexity_type/category breakdown. Read-only over
results/answers/*.jsonl: safe to run while script 04 is still writing other
arms' files, since each file is scored independently.

Usage:
    python scripts/05_score.py --scale 100 --split test
"""

import argparse
import json
import logging
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASETS_ROOT = ROOT / "datasets" / "mintaka"
sys.path.insert(0, str(ROOT))

from src.qa.mintaka_loader import load_split  # noqa: E402
from src.qa.qa_scorer import ScoredItem, aggregate_accuracy, score_answer  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

SPLIT_FILES = {"train": "mintaka_train.json", "dev": "mintaka_dev.json", "test": "mintaka_test.json"}
RESULTS_DIR = ROOT / "results" / "answers"
TABLES_DIR = ROOT / "results" / "tables"

FILENAME_RE = re.compile(r"^(?P<arm>.+)_(?P<scale>\d+|all)_seed(?P<seed>\d+)\.jsonl$")


def read_run_identity(path: Path, fallback: str, seed: int) -> dict:
    """Which arm, embedding model and LLM produced this file, read from the
    rows scripts/04 wrote rather than parsed out of the filename.

    Scans until it finds a row carrying the fields, rather than trusting the
    first line. An errored item is written as {"error": ...} with no run
    identity on it, so reading only the first line would report no arm for a
    run whose first question failed.
    """
    with open(path, encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            if "arm" in row:
                return {
                    "arm": row["arm"],
                    "embedding_model": row.get("embedding_model"),
                    "model": row.get("model"),
                    "seed": row.get("seed", seed),
                }
    return {"arm": None, "embedding_model": None, "model": None, "seed": seed, "identity_from": fallback}


def score_answer_file(path: Path, questions_by_id: dict) -> dict:
    items = []
    n_missing_gold = 0
    n_errors = 0
    n_truncated = 0
    by_answer_type: dict[str, list[bool]] = defaultdict(list)
    wall_clocks: list[float] = []
    energies: list[float] = []

    with open(path, encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            item_id = row["item_id"]
            q = questions_by_id.get(item_id)
            if q is None:
                n_missing_gold += 1
                continue
            # src/common/job_runner.py writes {"error": ...} for an item whose
            # worker raised. Scoring it would compare "" against gold and
            # count it wrong, charging an Ollama timeout to the model as a
            # wrong answer. Excluded and reported instead.
            if "error" in row:
                n_errors += 1
                continue

            correct = score_answer(
                row.get("generated_text", ""), q.answer_type, q.answer_labels_ar, q.answer_text,
                answer_labels_en=q.answer_labels_en,
            )
            items.append(ScoredItem(item_id=item_id, correct=correct, complexity_type=q.complexity_type, category=q.category))
            by_answer_type[q.answer_type].append(correct)

            if row.get("hit_token_cap"):
                n_truncated += 1
            if row.get("wall_clock_s") is not None:
                wall_clocks.append(row["wall_clock_s"])
            if row.get("gpu_energy_wh") is not None:
                energies.append(row["gpu_energy_wh"])

    if n_missing_gold:
        logger.warning("%s: %d rows had no matching gold item_id, skipped", path.name, n_missing_gold)
    if n_errors:
        logger.warning("%s: %d rows recorded an error, excluded rather than scored wrong", path.name, n_errors)

    scored = aggregate_accuracy(items)
    n = len(items)

    # scripts/04 records hit_token_cap per row so truncation shows up here.
    scored["truncated_rate"] = n_truncated / n if n else 0.0
    scored["n_truncated"] = n_truncated
    scored["n_errors"] = n_errors

    # Latency and energy, aggregated from scripts/04's per-row values.
    scored["mean_wall_clock_s"] = sum(wall_clocks) / len(wall_clocks) if wall_clocks else None
    scored["total_wall_clock_s"] = sum(wall_clocks) if wall_clocks else None
    scored["total_gpu_energy_wh"] = sum(energies) if energies else None

    # The non-entity matchers are rule-based (boolean matching is a word
    # list), so accuracy is broken out by answer type to show where a weak
    # number comes from.
    scored["by_answer_type"] = {
        k: {"accuracy": sum(v) / len(v), "n": len(v)} for k, v in sorted(by_answer_type.items())
    }
    return scored


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scale", required=True, help="100, 1000, 10000, or all")
    parser.add_argument("--split", default="test", choices=["train", "dev", "test"])
    args = parser.parse_args()

    questions = load_split(DATASETS_ROOT / SPLIT_FILES[args.split])
    questions_by_id = {q.id: q for q in questions}
    logger.info("%d gold questions loaded", len(questions_by_id))

    runs = {}
    for path in sorted((RESULTS_DIR / str(args.scale)).glob(f"*_{args.scale}_seed*.jsonl")):
        m = FILENAME_RE.match(path.name)
        if not m or m.group("scale") != str(args.scale):
            continue
        run_key = f"{m.group('arm')}|seed{m.group('seed')}"
        logger.info("scoring %s", path.name)
        scored = score_answer_file(path, questions_by_id)

        # Arm, embedding model and LLM come from the rows scripts/04 wrote,
        # not from the filename: the filename merges all three into one
        # string that cannot be split apart again, since sanitised model
        # names contain underscores. Falls back to the filename for a file
        # whose rows do not carry these fields.
        scored.update(read_run_identity(path, fallback=m.group("arm"), seed=int(m.group("seed"))))

        # A run still being written is scored on the rows that exist so far,
        # and a prefix is a biased sample, not just a small one: rows follow
        # the file order, so `generic` questions (20% of the split) sit at
        # the end. Mark the run rather than dropping it, so a partial tier
        # can still be inspected, and let scripts/06 keep it out of any
        # ranking.
        scored["complete"] = scored["n_items"] >= int(args.scale)
        if not scored["complete"]:
            logger.warning(
                "%s is incomplete: %d of %s rows. Marked complete=false; "
                "scripts/06 will exclude it from arm means and rankings.",
                path.name, scored["n_items"], args.scale,
            )
        runs[run_key] = scored

    out_dir = TABLES_DIR / str(args.scale)
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / f"scale_{args.scale}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"scale": args.scale, "runs": runs}, f, ensure_ascii=False, indent=2)
    logger.info("wrote %s (%d runs)", output_path, len(runs))


if __name__ == "__main__":
    main()
