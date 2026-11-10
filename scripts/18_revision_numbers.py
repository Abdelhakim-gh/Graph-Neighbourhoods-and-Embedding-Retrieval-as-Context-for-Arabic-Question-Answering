"""Numbers for the AICSET camera-ready revision (reviewer 1, points 1 to 3).

All new runs use the 1,000-question tier (select_scale(..., "1000")). Each is
compared, question by question, with the 4,000-question runs restricted to the
same 1,000 questions, scored with the same scorer as scripts/12.

  gold store, gold entities, 150 lines, 2 hops   none, graph, pooled, scoped (4,000-question runs)
  50-line budget                                  ctx_walk_answered_k50, ctx_pooled_answered_k50
  one hop                                         ctx_walk_answered_h1
  question-only store (no answer seeds)           ctx_walk_question, ctx_pooled_question, ctx_scoped_question
  predicted entities, question-only store         ctx_walk_predicted

Also, with no model calls: coverage at budgets 10 to 150 for the three context
arms over all 4,000 questions, coverage at one and two hops, the entity-linking
scores, and extra statistics for the six-model correlation.

  py -3.14 scripts/18_revision_numbers.py            # every run must be complete
  py -3.14 scripts/18_revision_numbers.py --partial  # questions answered so far
Writes results/tables/1000/revision_1000.json.
"""

import argparse
import itertools
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.qa.mintaka_loader import load_split, select_scale  # noqa: E402
from src.qa.qa_scorer import normalize_arabic, score_answer  # noqa: E402

ANS = ROOT / "results" / "answers"
MODELS = {"aya": "aya-expanse_8b", "qwen": "qwen3.5_9b"}
BASE = {  # 4,000-question runs, restricted to the tier
    "none": "no_retrieval_{m}_4000_seed1.jsonl",
    "graph": "graph_walk_{m}_4000_seed1.jsonl",
    "pooled": "retrieval_intfloat_multilingual-e5-large_{m}_4000_seed1.jsonl",
    "scoped": "ctx_scoped_answered_{m}_4000_seed1.jsonl",
}
NEW = {  # 1,000-question runs
    "graph_k50": "ctx_walk_answered_k50_{m}_1000_seed1.jsonl",
    "pooled_k50": "ctx_pooled_answered_k50_{m}_1000_seed1.jsonl",
    "graph_h1": "ctx_walk_answered_h1_{m}_1000_seed1.jsonl",
    "graph_q": "ctx_walk_question_{m}_1000_seed1.jsonl",
    "pooled_q": "ctx_pooled_question_{m}_1000_seed1.jsonl",
    "scoped_q": "ctx_scoped_question_{m}_1000_seed1.jsonl",
    "graph_pred": "ctx_walk_predicted_{m}_1000_seed1.jsonl",
}
# (arm, reference arm): the paired comparisons the paper reports.
COMPARE = [
    ("graph_k50", "graph"), ("pooled_k50", "pooled"), ("graph_k50", "pooled_k50"), ("graph", "pooled"),
    ("graph_h1", "graph"), ("graph_h1", "none"),
    ("graph_q", "graph"), ("pooled_q", "pooled"), ("scoped_q", "scoped"),
    ("graph_q", "pooled_q"), ("graph_q", "scoped_q"), ("scoped_q", "pooled_q"),
    ("graph_q", "none"), ("pooled_q", "none"), ("scoped_q", "none"),
    ("graph_pred", "graph_q"), ("graph_pred", "pooled_q"), ("graph_pred", "none"),
    ("graph", "scoped"), ("scoped", "pooled"), ("graph", "none"), ("pooled", "none"), ("scoped", "none"),
]


def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)


def pearson(x, y):
    mx, my = sum(x) / len(x), sum(y) / len(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    return sxy / math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))


def pct(k, n):
    return 100 * k / n if n else float("nan")


def load(path, qs, keep):
    if not path.exists():
        return None
    rows = {}
    for line in open(path, encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        if r["item_id"] not in keep:
            continue
        q = qs[r["item_id"]]
        rows[r["item_id"]] = {
            "correct": score_answer(r.get("generated_text", ""), q.answer_type, q.answer_labels_ar,
                                    q.answer_text, answer_labels_en=q.answer_labels_en),
            "ctx": normalize_arabic(r.get("context_used") or ""),
            "n_lines": len([s for s in (r.get("context_used") or "").split("\n") if s.strip()]),
            "cap": bool(r.get("hit_token_cap")), "s": r.get("wall_clock_s") or 0,
        }
    return rows


def has_gold(text_norm, q):
    return any(l and normalize_arabic(l) in text_norm for l in q.answer_labels_ar if l)


def coverage_curves(qs_all):
    """Coverage over all 4,000 questions at budgets 10 to 150, from the exact
    ranked contexts of the 4,000-question runs (no model calls)."""
    ent = [q for q in qs_all if q.answer_type == "entity" and any(q.answer_labels_ar)]
    budgets = [10, 25, 50, 100, 150]

    def dedup(xs):
        return list(dict.fromkeys(xs))

    sources = {}
    walk = {}
    for line in open(ROOT / "results/graph_walk/4000/walk_4000.jsonl", encoding="utf-8"):
        r = json.loads(line)
        walk[r["item_id"]] = dedup(s for p in r.get("paths", []) for s in p["sentences"])
    sources["graph"] = walk
    pooled = {}
    for line in open(ROOT / "results/retrieval/4000/intfloat_multilingual-e5-large_4000.jsonl", encoding="utf-8"):
        r = json.loads(line)
        pooled[r["item_id"]] = dedup(x["sentence"] for x in r["retrieved"])
    sources["pooled"] = pooled
    for name, fname in (("scoped", "scoped_answered"), ("graph_h1", "walk_answered_h1"),
                        ("graph_q", "walk_question"), ("pooled_q", "pooled_question"),
                        ("scoped_q", "scoped_question")):
        path = ROOT / "results/contexts/4000" / f"{fname}.jsonl"
        if path.exists():
            sources[name] = {r["item_id"]: r["lines"] for r in map(json.loads, open(path, encoding="utf-8"))}
    out = {}
    for name, ctx in sources.items():
        missing = [q.id for q in qs_all if q.id not in ctx]
        if missing:
            sys.exit(f"coverage source {name}: {len(missing)} questions missing")
        row = {}
        for k in budgets:
            hit = sum(has_gold(normalize_arabic("\n".join(ctx[q.id][:k])), q) for q in ent)
            row[k] = round(pct(hit, len(ent)), 1)
        out[name] = row
        print(f"   coverage {name:<9} " + "  ".join(f"top {k}: {v:5.1f}%" for k, v in row.items()))
    return {"n_entity_questions": len(ent), "budgets": out}


def six_model_stats():
    rows = [l.split() for l in open(ROOT / "paper-aicset-2026/figures/data_v2_six_models.dat", encoding="utf-8")][1:]
    x = [float(r[2]) for r in rows]
    y = [float(r[6]) for r in rows]
    r = pearson(x, y)
    z, se = math.atanh(r), 1 / math.sqrt(len(x) - 3)
    loo = {}
    for i, row in enumerate(rows):
        loo[row[0]] = round(pearson(x[:i] + x[i + 1:], y[:i] + y[i + 1:]), 2)
    res = {"pearson": round(r, 3), "fisher_95": [round(math.tanh(z - 1.96 * se), 2), round(math.tanh(z + 1.96 * se), 2)],
           "leave_one_out_r": loo}
    print(f"   six models: Pearson {r:.2f}, Fisher 95% interval {res['fisher_95'][0]:.2f} to {res['fisher_95'][1]:.2f}; "
          f"leave-one-out r {min(loo.values()):.2f} to {max(loo.values()):.2f}")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--partial", action="store_true")
    args = ap.parse_args()
    qs_all = load_split(ROOT / "datasets" / "mintaka" / "mintaka_test.json")
    qs = {q.id: q for q in qs_all}
    tier = [q.id for q in select_scale(qs_all, "1000")]
    keep = set(tier)
    report = {"tier_size": len(tier), "models": {}}

    for mk, stem in MODELS.items():
        runs = {a: load(ANS / "4000" / f.format(m=stem), qs, keep) for a, f in BASE.items()}
        runs.update({a: load(ANS / "1000" / f.format(m=stem), qs, keep) for a, f in NEW.items()})
        present = {a: r for a, r in runs.items() if r}
        if not args.partial:
            for a in list(BASE) + list(NEW):
                if a not in present or set(present[a]) != keep:
                    sys.exit(f"{mk} {a}: {len(present.get(a) or {})} of {len(tier)} questions; use --partial")
        elif "none" not in present:
            sys.exit(f"{mk}: the no-context run is missing")
        print("=" * 78)
        print(f"{mk}: " + ", ".join(f"{a} {len(r)}" for a, r in present.items()))
        m = report["models"][mk] = {"arms": {}, "pairs": {}}
        ent_all = [i for i in tier if qs[i].answer_type == "entity" and any(qs[i].answer_labels_ar)]
        for a, r in present.items():
            ids = [i for i in tier if i in r and i in present["none"]]
            ent = [i for i in ent_all if i in r and i in present["none"]]
            row = {"n": len(ids), "accuracy": round(pct(sum(r[i]["correct"] for i in ids), len(ids)), 2),
                   "mean_lines": round(sum(r[i]["n_lines"] for i in ids) / max(len(ids), 1), 1),
                   "token_cap": round(pct(sum(r[i]["cap"] for i in ids), len(ids)), 1),
                   "s_per_q": round(sum(r[i]["s"] for i in ids) / max(len(ids), 1), 2)}
            if a != "none":
                hit = [i for i in ent if has_gold(r[i]["ctx"], qs[i])]
                miss = [i for i in ent if not has_gold(r[i]["ctx"], qs[i])]
                k_ctx = sum(r[i]["correct"] for i in miss)
                k_none = sum(present["none"][i]["correct"] for i in miss)
                row.update(n_entity=len(ent), coverage=round(pct(len(hit), len(ent)), 1),
                           acc_present=round(pct(sum(r[i]["correct"] for i in hit), len(hit)), 1),
                           n_miss=len(miss), acc_miss=round(pct(k_ctx, len(miss)), 1),
                           none_miss=round(pct(k_none, len(miss)), 1),
                           # from the counts, rounded once (not a difference of rounded rates)
                           miss_cost=round(pct(k_ctx - k_none, len(miss)), 1))
            m["arms"][a] = row
            print(f"   {a:<11} " + "  ".join(f"{k} {v}" for k, v in row.items()))
        for a, b in COMPARE:
            if a in present and b in present:
                ids = [i for i in tier if i in present[a] and i in present[b]]
                oa = sum(1 for i in ids if present[a][i]["correct"] and not present[b][i]["correct"])
                ob = sum(1 for i in ids if present[b][i]["correct"] and not present[a][i]["correct"])
                d = {"n": len(ids), "diff": round(100 * (oa - ob) / len(ids), 2), "only_a": oa, "only_b": ob,
                     "p": float(f"{mcnemar_exact(oa, ob):.3g}")}
                m["pairs"][f"{a} - {b}"] = d
                print(f"   {a:>11} - {b:<11} {d['diff']:+6.2f} pts (n={len(ids)}, {oa} vs {ob})  p = {d['p']:.3g}")

    print("=" * 78)
    print("No model calls")
    report["coverage_curves_4000"] = coverage_curves(qs_all)
    report["six_models"] = six_model_stats()
    link = ROOT / "results/tables/1000/entity_linking_1000.json"
    if link.exists():
        report["entity_linking"] = json.loads(link.read_text(encoding="utf-8"))["overall"]
        o = report["entity_linking"]
        print(f"   entity linking: precision {o['micro_precision']:.3f}, recall {o['micro_recall']:.3f}, "
              f"all gold found {o['all_gold_found']:.3f}, at least one {o['at_least_one_gold_found']:.3f}, "
              f"no prediction {o['no_prediction']:.3f}")
    out = ROOT / "results/tables/1000" / ("revision_1000_partial.json" if args.partial else "revision_1000.json")
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
