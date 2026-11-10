"""Integrity review of the scoped-retrieval runs, before any number from
them is used.

1. Each run: 4,000 rows, unique item IDs, the same ID set as every archived
   4,000-question run, no error rows, the expected arm/context/model/seed.
2. The context each answer was generated with (`context_used`) equals the
   lines in results/contexts/4000/scoped_answered.jsonl, joined, for every row.
3. A fixed random sample of answers per model, printed with the question, the
   gold answer and the score, for a hand check of the scorer.

Run: py -3.14 scripts/14_review_scoped_runs.py
"""

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.qa.mintaka_loader import load_split  # noqa: E402
from src.qa.qa_scorer import score_answer  # noqa: E402

ANS = ROOT / "results" / "answers" / "4000"
MODELS = {"aya-expanse:8b": "aya-expanse_8b", "qwen3.5:9b": "qwen3.5_9b"}


def rows(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def main():
    qs = {q.id: q for q in load_split(ROOT / "datasets" / "mintaka" / "mintaka_test.json")}
    ctx = {r["item_id"]: "\n".join(r["lines"])
           for r in rows(ROOT / "results" / "contexts" / "4000" / "scoped_answered.jsonl")}
    reference_ids = {r["item_id"] for r in rows(ANS / "no_retrieval_aya-expanse_8b_4000_seed1.jsonl")}
    ok = True
    for model, stem in MODELS.items():
        rs = rows(ANS / f"ctx_scoped_answered_{stem}_4000_seed1.jsonl")
        ids = [r["item_id"] for r in rs]
        archived = [p for p in ANS.glob(f"*_{stem}_4000_seed1.jsonl") if not p.name.startswith("ctx_")]
        same_as_archived = all({r["item_id"] for r in rows(p)} == set(ids) for p in archived)
        errors = sum(1 for r in rs if r.get("error"))
        meta_bad = sum(1 for r in rs if r.get("arm") != "contexts" or r.get("context_name") != "scoped_answered"
                       or r.get("model") != model or r.get("seed") != 1)
        ctx_bad = sum(1 for r in rs if r.get("context_used", "") != ctx.get(r["item_id"]))
        checks = {
            "rows == 4000": len(rs) == 4000,
            "unique item ids": len(set(ids)) == len(ids),
            "same ids as the control": set(ids) == reference_ids,
            f"same ids as all {len(archived)} archived runs": same_as_archived,
            "no error rows": errors == 0,
            "arm/context/model/seed as expected": meta_bad == 0,
            "context_used equals the context file": ctx_bad == 0,
        }
        print(f"--- {model}")
        for name, passed in checks.items():
            print(f"   {'PASS' if passed else 'FAIL'}  {name}")
            ok &= passed
        if ctx_bad:
            print(f"   {ctx_bad} rows whose context differs from the file")

        print("   hand-check sample (seed 7):")
        rnd = random.Random(7)
        for r in rnd.sample(rs, 12):
            q = qs[r["item_id"]]
            gold = " | ".join(q.answer_labels_ar) if q.answer_labels_ar else (q.answer_text or "")
            sc = score_answer(r["generated_text"], q.answer_type, q.answer_labels_ar, q.answer_text,
                              answer_labels_en=q.answer_labels_en)
            print(f"     [{'correct' if sc else 'wrong  '}] {q.answer_type:<9} gold: {gold[:40]:<40} "
                  f"answer: {r['generated_text'][:50]!r}")
    print("\nALL CHECKS PASSED" if ok else "\nSOME CHECKS FAILED")


if __name__ == "__main__":
    main()
