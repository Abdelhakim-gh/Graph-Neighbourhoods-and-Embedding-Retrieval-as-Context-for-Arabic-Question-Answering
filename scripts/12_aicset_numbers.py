"""The paper's four-arm numbers.

Arms (scale 4000, both models), all on the answer-seeded store:
  none    archived no-context control
  graph   archived graph walk
  pooled  archived multilingual-E5 retrieval over all questions' facts
  scoped  ctx_scoped_answered: multilingual-E5 inside the walk's own pool

Prints: accuracy, exact
McNemar tests for every pair, coverage, miss-set accuracy against the same
model with no context, the exact two-part split for each pair of context arms,
the date and quantity line check, per-type gaps, cost, truncation, the worked
example, and the six-model check at 1,000 questions when its runs exist.
Writes the figure data files to paper-aicset-2026/figures/ (suffix _v2).

  py -3.14 scripts/12_aicset_numbers.py            # requires complete runs
  py -3.14 scripts/12_aicset_numbers.py --partial  # pilot: questions answered so far
"""

import argparse
import itertools
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.qa.graph_pull import drop_excluded_properties, scope_to_seeds  # noqa: E402
from src.qa.mintaka_loader import load_split, select_scale  # noqa: E402
from src.qa.qa_scorer import normalize_arabic, score_answer  # noqa: E402

ANS = ROOT / "results" / "answers"
FIG = ROOT / "paper-aicset-2026" / "figures"
MODELS4 = {"aya": "aya-expanse_8b", "qwen": "qwen3.5_9b"}
MODELS1 = {"aya-expanse:8b": "aya-expanse_8b", "command-r7b-arabic": "command-r7b-arabic_latest",
           "gemma4:12b": "gemma4_12b", "mistral-nemo:12b": "mistral-nemo_12b",
           "qwen3.5:4b": "qwen3.5_4b", "qwen3.5:9b": "qwen3.5_9b"}
# The answer-seeded store is the main design: a controlled setting in which a
# miss is a selection error rather than missing facts. Graph and pooled are
# the archived runs on that store; the scoped arm is built on the same store.
FILES = {
    "none": "no_retrieval_{m}_{s}_seed1.jsonl",
    "graph": "graph_walk_{m}_{s}_seed1.jsonl",
    "pooled": "retrieval_intfloat_multilingual-e5-large_{m}_{s}_seed1.jsonl",
    "scoped": "ctx_scoped_answered_{m}_{s}_seed1.jsonl",
}
PAIRS = [("graph", "pooled"), ("graph", "scoped"), ("scoped", "pooled"),
         ("graph", "none"), ("pooled", "none"), ("scoped", "none")]


def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)


def pearson(x, y):
    mx, my = sum(x) / len(x), sum(y) / len(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    return sxy / math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for t in range(i, j + 1):
            r[order[t]] = (i + j) / 2 + 1
        i = j + 1
    return r


def perm_p(x, y, stat):
    obs = abs(stat(x, y))
    perms = list(itertools.permutations(y))
    return sum(abs(stat(x, list(p))) >= obs - 1e-12 for p in perms) / len(perms)


def load_run(qs, scale, arm, stem):
    path = ANS / str(scale) / FILES[arm].format(m=stem, s=scale)
    if not path.exists():
        return None
    rows = {}
    for line in open(path, encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            q = qs[r["item_id"]]
            r["correct"] = score_answer(r.get("generated_text", ""), q.answer_type, q.answer_labels_ar,
                                        q.answer_text, answer_labels_en=q.answer_labels_en)
            r["ctx_norm"] = normalize_arabic(r.get("context_used") or "")
            rows[r["item_id"]] = r
    return rows


def covered(r, q):
    return any(l and normalize_arabic(l) in r["ctx_norm"] for l in q.answer_labels_ar if l)


def pct(k, n):
    return 100 * k / n if n else float("nan")


def split_terms(runs, a, b, ent, qs):
    """Exact split of acc(a) - acc(b) on `ent` into in-context and absent terms."""
    n = len(ent)
    t = {}
    for arm in (a, b):
        hit = [i for i in ent if covered(runs[arm][i], qs[i])]
        miss = [i for i in ent if not covered(runs[arm][i], qs[i])]
        t[arm] = (sum(runs[arm][i]["correct"] for i in hit), sum(runs[arm][i]["correct"] for i in miss))
    return 100 * (t[a][0] - t[b][0]) / n, 100 * (t[a][1] - t[b][1]) / n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--partial", action="store_true")
    args = ap.parse_args()
    qs = {q.id: q for q in load_split(ROOT / "datasets" / "mintaka" / "mintaka_test.json")}
    fig_rows = {}

    print("=" * 78)
    print("SCALE 4000, answer-seeded store" + ("  [PARTIAL]" if args.partial else ""))
    for mk, stem in MODELS4.items():
        runs = {arm: load_run(qs, 4000, arm, stem) for arm in FILES}
        present = [a for a in ("none", "graph", "pooled", "scoped") if runs[a]]
        ids = sorted(set.intersection(*(set(runs[a]) for a in present)))
        if not args.partial and len(ids) < 4000:
            sys.exit(f"{mk}: only {len(ids)} paired questions; run with --partial for a pilot view")
        print(f"\n--- {mk}: arms {present}, paired questions {len(ids)}")
        acc = {a: pct(sum(runs[a][i]["correct"] for i in ids), len(ids)) for a in present}
        for a in present:
            print(f"   accuracy {a:<7} {acc[a]:6.2f}%")
        for a, b in PAIRS:
            if a in present and b in present:
                oa = sum(1 for i in ids if runs[a][i]["correct"] and not runs[b][i]["correct"])
                ob = sum(1 for i in ids if runs[b][i]["correct"] and not runs[a][i]["correct"])
                print(f"   {a:>6} - {b:<6} {100 * (oa - ob) / len(ids):+6.2f} pts  "
                      f"(only {a} {oa}, only {b} {ob})  McNemar p = {mcnemar_exact(oa, ob):.2g}")

        ent = [i for i in ids if qs[i].answer_type == "entity" and any(qs[i].answer_labels_ar)]
        print(f"   entity questions with an Arabic gold label: {len(ent)}")
        for a in present:
            if a == "none":
                continue
            hit = [i for i in ent if covered(runs[a][i], qs[i])]
            miss = [i for i in ent if not covered(runs[a][i], qs[i])]
            print(f"   {a:<7} coverage {pct(len(hit), len(ent)):5.1f}%  | answer present: "
                  f"{pct(sum(runs[a][i]['correct'] for i in hit), len(hit)):5.1f}% correct  | miss set n={len(miss)}: "
                  f"{pct(sum(runs[a][i]['correct'] for i in miss), len(miss)):5.1f}% with context vs "
                  f"{pct(sum(runs['none'][i]['correct'] for i in miss), len(miss)):5.1f}% no context")
            fig_rows.setdefault("coverage", []).append((mk, a, pct(len(hit), len(ent)),
                                                       pct(sum(runs[a][i]['correct'] for i in miss), len(miss)),
                                                       pct(sum(runs['none'][i]['correct'] for i in miss), len(miss)),
                                                       len(miss)))
        for a, b in (("graph", "pooled"), ("graph", "scoped"), ("scoped", "pooled")):
            if a in present and b in present:
                inc, absn = split_terms(runs, a, b, ent, qs)
                print(f"   split {a}-{b}: answer in context {inc:+6.2f}, answer absent {absn:+6.2f}, "
                      f"total {inc + absn:+6.2f}")
                fig_rows.setdefault("split", []).append((mk, f"{a}-{b}", inc, absn))
        fig_rows.setdefault("headline", []).append((mk, *(acc.get(a, float("nan")) for a in ("none", "pooled", "scoped", "graph"))))

        # Entity-answer questions only: a date or quantity line cannot be the answer.
        if "graph" in present and "pooled" in present:
            ea = [i for i in ids if qs[i].answer_type == "entity"]
            oa = sum(1 for i in ea if runs["graph"][i]["correct"] and not runs["pooled"][i]["correct"])
            ob = sum(1 for i in ea if runs["pooled"][i]["correct"] and not runs["graph"][i]["correct"])
            print(f"   entity-answer questions n={len(ea)}: graph - pooled {100 * (oa - ob) / len(ea):+5.2f} "
                  f"p = {mcnemar_exact(oa, ob):.2g}")

        # Every pair of context arms by answer type, and on entity answers only,
        # where a date or quantity line (pooled arm only) cannot be the answer.
        for a, b in (("graph", "pooled"), ("graph", "scoped"), ("scoped", "pooled")):
            if a in present and b in present:
                parts = []
                for t in ("entity", "boolean", "numerical", "date"):
                    sub = [i for i in ids if qs[i].answer_type == t]
                    oa = sum(1 for i in sub if runs[a][i]["correct"] and not runs[b][i]["correct"])
                    ob = sum(1 for i in sub if runs[b][i]["correct"] and not runs[a][i]["correct"])
                    parts.append(f"{t} n={len(sub)} {100 * (oa - ob) / len(sub):+5.1f} (p={mcnemar_exact(oa, ob):.2g})")
                print(f"   by answer type {a}-{b}: " + "; ".join(parts))

        # Per complexity type, graph minus each retrieval arm.
        by_type = defaultdict(list)
        for i in ids:
            by_type[qs[i].complexity_type].append(i)
        for b in ("pooled", "scoped"):
            if "graph" in present and b in present:
                row = {t: pct(sum(runs["graph"][i]["correct"] for i in v) - sum(runs[b][i]["correct"] for i in v), len(v))
                       for t, v in by_type.items()}
                print(f"   per type graph-{b}: " + ", ".join(f"{t} {d:+.1f}" for t, d in sorted(row.items(), key=lambda x: -x[1])))
                fig_rows.setdefault("types", []).append((mk, b, row))

        for a in present:
            rs = [runs[a][i] for i in ids]
            print(f"   cost {a:<7} {sum(r.get('gpu_energy_wh') or 0 for r in rs):7.1f} Wh  "
                  f"{sum(r.get('wall_clock_s') or 0 for r in rs) / len(rs):.2f} s/q  "
                  f"token cap {pct(sum(bool(r.get('hit_token_cap')) for r in rs), len(rs)):.1f}%  "
                  f"median prompt {sorted(r.get('tokens_in') or 0 for r in rs)[len(rs) // 2]}  "
                  f"max prompt {max(r.get('tokens_in') or 0 for r in rs)}")

        if "b2ee87db" in ids:
            q = qs["b2ee87db"]
            gold = [normalize_arabic(l) for l in q.answer_labels_ar if l]
            for a in present:
                r = runs[a]["b2ee87db"]
                lines = [l for l in (r.get("context_used") or "").split("\n") if l.strip()]
                at = [k + 1 for k, l in enumerate(lines) if any(g in normalize_arabic(l) for g in gold)]
                second = sum(1 for l in lines if "الثاني" in l or "الثانية" in l)
                print(f"   example b2ee87db {a:<7} correct={r['correct']}  gold at line {at or 'none'}  "
                      f"lines with 'second' {second}/{len(lines)}  answer: {r['generated_text'][:40]!r}")

    # Six models at 1,000 questions.
    print("\n" + "=" * 78)
    print("SCALE 1000, six models, answer-seeded store (archived graph and pooled arms)")
    six = []
    for label, stem in MODELS1.items():
        runs = {a: load_run(qs, 1000, a, stem) for a in ("none", "graph", "pooled")}
        if not all(runs.values()):
            print(f"   {label}: runs not complete yet")
            continue
        ids = sorted(set.intersection(*(set(v) for v in runs.values())))
        if not args.partial and len(ids) < 1000:
            print(f"   {label}: only {len(ids)} paired questions")
            continue
        ent = [i for i in ids if qs[i].answer_type == "entity" and any(qs[i].answer_labels_ar)]
        inc, absn = split_terms(runs, "graph", "pooled", ent, qs)
        oa = sum(1 for i in ids if runs["graph"][i]["correct"] and not runs["pooled"][i]["correct"])
        ob = sum(1 for i in ids if runs["pooled"][i]["correct"] and not runs["graph"][i]["correct"])
        d = dict(model=label, n=len(ids), none=pct(sum(runs["none"][i]["correct"] for i in ids), len(ids)),
                 gap=100 * (oa - ob) / len(ids), p=mcnemar_exact(oa, ob),
                 unaided_ent=pct(sum(runs["none"][i]["correct"] for i in ent), len(ent)),
                 in_ctx=inc, absent=absn, ent_gap=inc + absn, n_ent=len(ent))
        six.append(d)
        print(f"   {label:<20} n={d['n']} unaided(ent) {d['unaided_ent']:5.1f}%  gap(all) {d['gap']:+5.2f} "
              f"p={d['p']:.2g}  ent: in-ctx {inc:+5.2f} absent {absn:+5.2f} total {inc + absn:+5.2f}")
    if len(six) == 6:
        spear = lambda a, b: pearson(ranks(a), ranks(b))  # noqa: E731
        for xl, xk, yl, yk in (("unaided(ent)", "unaided_ent", "gap(ent)", "ent_gap"),
                               ("unaided(all)", "none", "gap(all)", "gap"),
                               ("unaided(ent)", "unaided_ent", "absent term", "absent"),
                               ("unaided(ent)", "unaided_ent", "in-context term", "in_ctx")):
            x, y = [d[xk] for d in six], [d[yk] for d in six]
            print(f"   {xl} vs {yl}: Pearson {pearson(x, y):+.2f} (p={perm_p(x, y, pearson):.3f})  "
                  f"Spearman {spear(x, y):+.2f} (p={perm_p(x, y, spear):.3f})")
        x, y = [d["unaided_ent"] for d in six], [d["ent_gap"] for d in six]
        mx, my = sum(x) / 6, sum(y) / 6
        slope = sum((a - mx) * (b - my) for a, b in zip(x, y)) / sum((a - mx) ** 2 for a in x)
        print(f"   least-squares fit: gap = {my - slope * mx:.3f} + {slope:.3f} x unaided")
        fig_rows["six"] = six

    if not args.partial:
        FIG.mkdir(parents=True, exist_ok=True)
        with open(FIG / "data_v2_headline.dat", "w", encoding="utf-8", newline="\n") as f:
            f.write("model none pooled scoped graph\n")
            for r in fig_rows["headline"]:
                f.write(" ".join([r[0]] + [f"{v:.2f}" for v in r[1:]]) + "\n")
        with open(FIG / "data_v2_coverage.dat", "w", encoding="utf-8", newline="\n") as f:
            f.write("model arm coverage acc_miss none_miss n_miss\n")
            for r in fig_rows["coverage"]:
                f.write(f"{r[0]} {r[1]} {r[2]:.2f} {r[3]:.2f} {r[4]:.2f} {r[5]}\n")
        with open(FIG / "data_v2_split.dat", "w", encoding="utf-8", newline="\n") as f:
            f.write("model pair answer_in_context answer_absent total\n")
            for m, pair, inc, absn in fig_rows["split"]:
                f.write(f"{m} {pair} {inc:.2f} {absn:.2f} {inc + absn:.2f}\n")
        with open(FIG / "data_v2_types.dat", "w", encoding="utf-8", newline="\n") as f:
            f.write("model versus type gap\n")
            for m, b, row in fig_rows["types"]:
                for t, d in sorted(row.items(), key=lambda x: -x[1]):
                    f.write(f"{m} {b} {t} {d:.2f}\n")
        if "six" in fig_rows:
            with open(FIG / "data_v2_six_models.dat", "w", encoding="utf-8", newline="\n") as f:
                f.write("model none unaided_ent gap in_ctx absent ent_gap p\n")
                for d in fig_rows["six"]:
                    f.write(f"{d['model']} {d['none']:.2f} {d['unaided_ent']:.2f} {d['gap']:.2f} "
                            f"{d['in_ctx']:.2f} {d['absent']:.2f} {d['ent_gap']:.2f} {d['p']:.3g}\n")
        print(f"\nwrote figure data to {FIG.relative_to(ROOT)}/data_v2_*.dat")


if __name__ == "__main__":
    main()
