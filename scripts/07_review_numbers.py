"""Significance tests and supporting numbers for the paper.

Everything is computed from the six scale-4000 answer files, re-scored with
src/qa/qa_scorer.py exactly as scripts/05_score.py does, so the headline
accuracies must reproduce first; the script stops if they do not.

1. Exact McNemar tests for every arm-to-arm gap, per model.
2. The coverage table (gold label in context) on entity questions whose gold has
   an Arabic label, reproduced, then the two "price" counterfactuals of Fig. 3a
   computed two ways: as the paper did, and like for like.
3. The date and quantity lines in the retrieval arm's context, which the graph
   walk could not reach, and accuracy with and without them.

Run: py -3.14 scripts/07_review_numbers.py
"""

import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.qa.mintaka_loader import load_split  # noqa: E402
from src.qa.qa_scorer import extract_numbers, normalize_arabic, score_answer  # noqa: E402

ANS = ROOT / "results" / "answers" / "4000"
RUNS = {
    ("none", "aya"): "no_retrieval_aya-expanse_8b_4000_seed1.jsonl",
    ("none", "qwen"): "no_retrieval_qwen3.5_9b_4000_seed1.jsonl",
    ("graph", "aya"): "graph_walk_aya-expanse_8b_4000_seed1.jsonl",
    ("graph", "qwen"): "graph_walk_qwen3.5_9b_4000_seed1.jsonl",
    ("retr", "aya"): "retrieval_intfloat_multilingual-e5-large_aya-expanse_8b_4000_seed1.jsonl",
    ("retr", "qwen"): "retrieval_intfloat_multilingual-e5-large_qwen3.5_9b_4000_seed1.jsonl",
}
EXPECTED = {("none", "aya"): 30.53, ("graph", "aya"): 36.38, ("retr", "aya"): 31.72,
            ("none", "qwen"): 18.85, ("graph", "qwen"): 30.38, ("retr", "qwen"): 31.95}


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def main():
    qs = {q.id: q for q in load_split(ROOT / "datasets" / "mintaka" / "mintaka_test.json")}
    correct, context, texts = {}, {}, {}
    for key, name in RUNS.items():
        rows = read_jsonl(ANS / name)
        correct[key] = {}
        context[key] = {}
        texts[key] = {}
        for r in rows:
            q = qs[r["item_id"]]
            correct[key][r["item_id"]] = score_answer(
                r.get("generated_text", ""), q.answer_type, q.answer_labels_ar, q.answer_text,
                answer_labels_en=q.answer_labels_en)
            context[key][r["item_id"]] = r.get("context_used") or ""
            texts[key][r["item_id"]] = r.get("generated_text", "")
    ids = sorted(set.intersection(*(set(v) for v in correct.values())))
    print(f"paired items: {len(ids)}")
    print("0. HEADLINE ACCURACIES (must reproduce the paper)")
    for key in RUNS:
        acc = 100 * sum(correct[key][i] for i in ids) / len(ids)
        flag = "ok" if abs(acc - EXPECTED[key]) < 0.01 else "MISMATCH"
        print(f"   {key[0]:<6}{key[1]:<5}{acc:6.2f}%  {flag}")
        if flag != "ok":
            sys.exit("headline accuracies do not reproduce; stopping")

    print()
    print("1. EXACT McNEMAR, PAIRED OVER ALL 4,000 QUESTIONS")
    for model in ("aya", "qwen"):
        for a, b in (("graph", "retr"), ("graph", "none"), ("retr", "none")):
            A, B = correct[(a, model)], correct[(b, model)]
            only_a = sum(1 for i in ids if A[i] and not B[i])
            only_b = sum(1 for i in ids if B[i] and not A[i])
            gap = 100 * (only_a - only_b) / len(ids)
            print(f"   {model:<5}{a:>6} vs {b:<6} gap {gap:+6.2f} pts   "
                  f"only {a} {only_a:4d}, only {b} {only_b:4d}   p = {mcnemar_exact(only_a, only_b):.2g}")

    print()
    print("2. COVERAGE AND THE TWO COUNTERFACTUALS (Fig. 3a)")
    ent = [i for i in ids if qs[i].answer_type == "entity" and any(qs[i].answer_labels_ar)]
    print(f"   entity questions with an Arabic gold label: {len(ent)}")

    def covered(key, i, norm):
        ctx = context[key][i]
        labels = [l for l in qs[i].answer_labels_ar if l]
        if norm:
            ctx = normalize_arabic(ctx)
            labels = [normalize_arabic(l) for l in labels]
        return any(l and l in ctx for l in labels)

    for norm in (False, True):
        cg = [i for i in ent if covered(("graph", "aya"), i, norm)]
        cr = [i for i in ent if covered(("retr", "aya"), i, norm)]
        print(f"   normalised={norm!s:<5} graph coverage {100*len(cg)/len(ent):5.1f}%  "
              f"retrieval coverage {100*len(cr)/len(ent):5.1f}%  "
              f"graph misses {len(ent)-len(cg)}  retrieval misses {len(ent)-len(cr)}")
    norm = True  # the paper's 66.7 / 76.5 and 715 / 504 reproduce only with normalised matching

    def rate(key, subset):
        return 100 * sum(correct[key][i] for i in subset) / len(subset) if subset else float("nan")

    for model in ("aya", "qwen"):
        g, r, n0 = ("graph", model), ("retr", model), ("none", model)
        g_hit = [i for i in ent if covered(g, i, norm)]
        g_miss = [i for i in ent if not covered(g, i, norm)]
        r_hit = [i for i in ent if covered(r, i, norm)]
        r_miss = [i for i in ent if not covered(r, i, norm)]
        cov_g, cov_r = len(g_hit) / len(ent), len(r_hit) / len(ent)
        print(f"   {model}: graph hit {rate(g, g_hit):5.1f}% miss {rate(g, g_miss):5.1f}% "
              f"(no-context on graph misses {rate(n0, g_miss):5.1f}%) | "
              f"retrieval hit {rate(r, r_hit):5.1f}% miss {rate(r, r_miss):5.1f}% "
              f"(no-context on retrieval misses {rate(n0, r_miss):5.1f}%)")
        coverage_price = (cov_r - cov_g) * (rate(g, g_hit) - rate(g, g_miss))
        damage_as_paper = (1 - cov_r) * (rate(g, g_miss) - rate(r, r_miss))
        graph_damage = rate(g, g_miss) - rate(n0, g_miss)
        damage_like_for_like = (1 - cov_r) * ((rate(n0, r_miss) + graph_damage) - rate(r, r_miss))
        print(f"      coverage price {coverage_price:5.2f}   damage price as in the paper {damage_as_paper:5.2f}"
              f"   damage price like for like {damage_like_for_like:5.2f}")
        observed = rate(g, ent) - rate(r, ent)
        print(f"      observed graph minus retrieval on these {len(ent)} questions: {observed:+5.2f} pts")

    print()
    print("3. DATE AND QUANTITY LINES IN THE RETRIEVAL CONTEXT")
    retr = {r["item_id"]: r["retrieved"] for r in
            read_jsonl(ROOT / "results" / "retrieval" / "4000" / "intfloat_multilingual-e5-large_4000.jsonl")}
    lit_share = []
    has_lit = set()
    for i in ids:
        lines = retr.get(i, [])
        k = sum(1 for x in lines if not x.get("tail_qid"))
        if lines:
            lit_share.append(k / len(lines))
        if k:
            has_lit.add(i)
    print(f"   mean share of retrieved lines that are date/quantity facts: {100*sum(lit_share)/len(lit_share):.1f}%")
    print(f"   questions whose retrieved context holds at least one: {len(has_lit)} of {len(ids)}")
    by_type = defaultdict(lambda: [0, 0])
    for i in ids:
        by_type[qs[i].answer_type][0] += 1
        by_type[qs[i].answer_type][1] += i in has_lit
    for t, (n, k) in sorted(by_type.items()):
        print(f"      answer type {t:<10} {k:5d} of {n:5d}")
    for model in ("aya", "qwen"):
        for t in ("date", "numerical", "boolean", "entity"):
            sub = [i for i in ids if qs[i].answer_type == t]
            g, r = rate(("graph", model), sub), rate(("retr", model), sub)
            print(f"   {model:<5}{t:<10} n={len(sub):5d}  graph {g:5.1f}%  retrieval {r:5.1f}%  "
                  f"graph minus retrieval {g - r:+5.1f}")
    print("   graph minus retrieval restricted to entity-answer questions, where a date or")
    print("   quantity line cannot itself be the answer:")
    ent_all = [i for i in ids if qs[i].answer_type == "entity"]
    for model in ("aya", "qwen"):
        g, r = correct[("graph", model)], correct[("retr", model)]
        oa = sum(1 for i in ent_all if g[i] and not r[i])
        ob = sum(1 for i in ent_all if r[i] and not g[i])
        print(f"      {model:<5} n={len(ent_all)}  {100*(oa-ob)/len(ent_all):+5.2f} pts   p = {mcnemar_exact(oa, ob):.2g}")
    nonent = [i for i in ids if qs[i].answer_type != "entity"]
    for model in ("aya", "qwen"):
        g, r = correct[("graph", model)], correct[("retr", model)]
        oa = sum(1 for i in nonent if g[i] and not r[i])
        ob = sum(1 for i in nonent if r[i] and not g[i])
        print(f"      {model:<5} non-entity n={len(nonent)}  {100*(oa-ob)/len(nonent):+5.2f} pts   "
              f"p = {mcnemar_exact(oa, ob):.2g}")

    # Share of numerical answers stating two or more numbers, per arm and
    # model. For aya-expanse:8b this gives 15.9 / 5.3 / 3.7% (no context /
    # graph / retrieval); qwen3.5:9b gives 12.1 / 9.8 / 4.6.
    print()
    print("4. NUMERICAL ANSWERS STATING TWO OR MORE NUMBERS (scorer's extract_numbers)")
    numq = [i for i in ids if qs[i].answer_type == "numerical"]
    for arm in ("none", "graph", "retr"):
        per = []
        tot = multi = 0
        for model in ("aya", "qwen"):
            k = sum(1 for i in numq if len(set(extract_numbers(texts[(arm, model)][i]))) >= 2)
            per.append(f"{model} {100*k/len(numq):4.1f}%")
            tot += len(numq)
            multi += k
        print(f"   {arm:<6} pooled {100*multi/tot:4.1f}% of {tot}   ({', '.join(per)})")


if __name__ == "__main__":
    main()
