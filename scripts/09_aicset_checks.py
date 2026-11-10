"""Data checks behind statements in the paper that no other script
regenerates.

1. The worked example (Mintaka b2ee87db, Table 1): each arm's answer and
   whether it is correct, the line holding the gold answer in each context,
   and how many retrieved lines contain the Arabic word for "second".
2. Graph contexts: mean distinct lines and the number of empty contexts.
3. Energy and time per question per arm on aya-expanse:8b.
4. Token-cap share per arm on qwen3.5:9b.

The multi-number shares are in scripts/07_review_numbers.py (section 4) and the
six-model figures in scripts/08_six_model_trend.py.

Run: py -3.14 scripts/09_aicset_checks.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.qa.mintaka_loader import load_split  # noqa: E402
from src.qa.qa_scorer import normalize_arabic, score_answer  # noqa: E402

ANS = ROOT / "results" / "answers" / "4000"
ARMS = {
    "control": "no_retrieval_{m}_4000_seed1.jsonl",
    "graph": "graph_walk_{m}_4000_seed1.jsonl",
    "retrieval": "retrieval_intfloat_multilingual-e5-large_{m}_4000_seed1.jsonl",
}
EXAMPLE = "b2ee87db"


def rows(arm, model):
    with open(ANS / ARMS[arm].format(m=model), encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def lines_of(r):
    return [l for l in (r.get("context_used") or "").split("\n") if l.strip()]


def main():
    qs = {q.id: q for q in load_split(ROOT / "datasets" / "mintaka" / "mintaka_test.json")}

    print("1. WORKED EXAMPLE", EXAMPLE, "on aya-expanse:8b")
    q = qs[EXAMPLE]
    gold = [normalize_arabic(l) for l in q.answer_labels_ar if l]
    for arm in ARMS:
        r = next(x for x in rows(arm, "aya-expanse_8b") if x["item_id"] == EXAMPLE)
        ok = score_answer(r["generated_text"], q.answer_type, q.answer_labels_ar, q.answer_text,
                          answer_labels_en=q.answer_labels_en)
        ls = lines_of(r)
        hit = [i + 1 for i, l in enumerate(ls) if any(g in normalize_arabic(l) for g in gold)]
        second = sum(1 for l in ls if "الثاني" in l or "الثانية" in l)
        print(f"   {arm:<10} correct={ok}  lines={len(ls)}  gold at line(s) {hit or 'none'}  "
              f"lines with 'second': {second}")

    print("\n2. GRAPH CONTEXT SIZE (aya-expanse:8b run; contexts are model-independent)")
    counts = [len({l.strip() for l in lines_of(r)}) for r in rows("graph", "aya-expanse_8b")]
    print(f"   mean distinct lines {sum(counts) / len(counts):.1f}, empty contexts {sum(c == 0 for c in counts)}")

    print("\n3. ENERGY AND TIME, aya-expanse:8b")
    for arm in ARMS:
        rs = rows(arm, "aya-expanse_8b")
        wh = sum(r.get("gpu_energy_wh") or 0 for r in rs)
        s = sum(r.get("wall_clock_s") or 0 for r in rs) / len(rs)
        print(f"   {arm:<10} {wh:6.1f} Wh   {s:.2f} s per question")

    print("\n4. TOKEN CAP, qwen3.5:9b")
    for arm in ARMS:
        rs = rows(arm, "qwen3.5_9b")
        print(f"   {arm:<10} {100 * sum(bool(r.get('hit_token_cap')) for r in rs) / len(rs):.1f}%")


if __name__ == "__main__":
    main()
