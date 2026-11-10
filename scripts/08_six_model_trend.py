"""Does the graph-versus-retrieval ranking follow the model's unaided accuracy?

At scale 4000 the claim rests on two models. The scale-1000 tier ran six
models on the same three arms (no context, graph walk, multilingual-E5
retrieval), so the claim can be checked on six points without new GPU runs.

For each model this script re-scores the three scale-1000 runs with
src/qa/qa_scorer.py, then reports:

1. accuracy per arm, and graph minus retrieval with an exact McNemar test;
2. on entity questions whose gold has an Arabic label, coverage per arm and
   the exact split of graph minus retrieval into questions answered with the
   answer in context and questions answered without it (the split of Fig. 3a
   in the scale-4000 paper);
3. unaided (no-context) accuracy on each arm's miss set;
4. Spearman and Pearson correlation across the six models between unaided
   accuracy and the graph-minus-retrieval gap, with exact permutation p-values
   (720 orderings, so nothing is approximated).

The two scale-4000 models are printed with the same code as a check.
Writes paper-aicset-2026/figures/data_six_models.dat.

Run: py -3.14 scripts/08_six_model_trend.py
"""

import itertools
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.qa.mintaka_loader import load_split  # noqa: E402
from src.qa.qa_scorer import normalize_arabic, score_answer  # noqa: E402

MODELS_1000 = {
    "aya-expanse:8b": "aya-expanse_8b",
    "command-r7b-arabic": "command-r7b-arabic_latest",
    "gemma4:12b": "gemma4_12b",
    "mistral-nemo:12b": "mistral-nemo_12b",
    "qwen3.5:4b": "qwen3.5_4b",
    "qwen3.5:9b": "qwen3.5_9b",
}
MODELS_4000 = {"aya-expanse:8b": "aya-expanse_8b", "qwen3.5:9b": "qwen3.5_9b"}
E5 = "intfloat_multilingual-e5-large"


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def pearson(x, y):
    mx, my = sum(x) / len(x), sum(y) / len(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    return sxy / math.sqrt(sxx * syy)


def perm_p(x, y, stat):
    """Two-sided exact permutation p-value over every ordering of y."""
    obs = abs(stat(x, y))
    hits = total = 0
    for perm in itertools.permutations(y):
        total += 1
        hits += abs(stat(x, list(perm))) >= obs - 1e-12
    return hits / total


def analyse(qs, scale, models):
    ans = ROOT / "results" / "answers" / str(scale)
    out = []
    for label, stem in models.items():
        files = {
            "none": ans / f"no_retrieval_{stem}_{scale}_seed1.jsonl",
            "graph": ans / f"graph_walk_{stem}_{scale}_seed1.jsonl",
            "retr": ans / f"retrieval_{E5}_{stem}_{scale}_seed1.jsonl",
        }
        correct, ctx = {}, {}
        for arm, path in files.items():
            correct[arm], ctx[arm] = {}, {}
            for r in read_jsonl(path):
                q = qs[r["item_id"]]
                correct[arm][r["item_id"]] = score_answer(
                    r.get("generated_text", ""), q.answer_type, q.answer_labels_ar, q.answer_text,
                    answer_labels_en=q.answer_labels_en)
                ctx[arm][r["item_id"]] = normalize_arabic(r.get("context_used") or "")
        ids = sorted(set.intersection(*(set(v) for v in correct.values())))
        acc = {a: 100 * sum(correct[a][i] for i in ids) / len(ids) for a in files}
        only_g = sum(1 for i in ids if correct["graph"][i] and not correct["retr"][i])
        only_r = sum(1 for i in ids if correct["retr"][i] and not correct["graph"][i])

        ent = [i for i in ids if qs[i].answer_type == "entity" and any(qs[i].answer_labels_ar)]

        def covered(arm, i):
            labels = [normalize_arabic(l) for l in qs[i].answer_labels_ar if l]
            return any(l and l in ctx[arm][i] for l in labels)

        hit = {a: [i for i in ent if covered(a, i)] for a in ("graph", "retr")}
        miss = {a: [i for i in ent if not covered(a, i)] for a in ("graph", "retr")}
        n = len(ent)
        cnt = lambda arm, subset: sum(correct[arm][i] for i in subset)  # noqa: E731
        in_ctx = 100 * (cnt("graph", hit["graph"]) - cnt("retr", hit["retr"])) / n
        absent = 100 * (cnt("graph", miss["graph"]) - cnt("retr", miss["retr"])) / n
        unaided_gmiss = 100 * cnt("none", miss["graph"]) / len(miss["graph"])
        unaided_rmiss = 100 * cnt("none", miss["retr"]) / len(miss["retr"])
        with_gmiss = 100 * cnt("graph", miss["graph"]) / len(miss["graph"])
        with_rmiss = 100 * cnt("retr", miss["retr"]) / len(miss["retr"])
        out.append(dict(
            model=label, n=len(ids), none=acc["none"], graph=acc["graph"], retr=acc["retr"],
            gap=acc["graph"] - acc["retr"], p=mcnemar_exact(only_g, only_r),
            n_ent=n, cov_g=100 * len(hit["graph"]) / n, cov_r=100 * len(hit["retr"]) / n,
            in_ctx=in_ctx, absent=absent, ent_gap=in_ctx + absent,
            unaided_ent=100 * cnt("none", ent) / n,
            unaided_gmiss=unaided_gmiss, unaided_rmiss=unaided_rmiss,
            with_gmiss=with_gmiss, with_rmiss=with_rmiss,
            n_gmiss=len(miss["graph"]), n_rmiss=len(miss["retr"]),
        ))
    return out


def show(rows, title):
    print(title)
    print(f"   {'model':<20}{'n':>5}{'none':>7}{'graph':>7}{'retr':>7}{'g-r':>7}{'p':>9}"
          f" | {'ent':>5}{'covG':>6}{'covR':>6}{'inCtx':>7}{'absent':>7}"
          f"{'unaidGm':>8}{'withGm':>7}{'unaidRm':>8}{'withRm':>7}")
    for r in rows:
        print(f"   {r['model']:<20}{r['n']:>5}{r['none']:>7.1f}{r['graph']:>7.1f}{r['retr']:>7.1f}"
              f"{r['gap']:>+7.1f}{r['p']:>9.2g} | {r['n_ent']:>5}{r['cov_g']:>6.1f}{r['cov_r']:>6.1f}"
              f"{r['in_ctx']:>+7.2f}{r['absent']:>+7.2f}{r['unaided_gmiss']:>8.1f}{r['with_gmiss']:>7.1f}"
              f"{r['unaided_rmiss']:>8.1f}{r['with_rmiss']:>7.1f}")


def main():
    qs = {q.id: q for q in load_split(ROOT / "datasets" / "mintaka" / "mintaka_test.json")}
    six = analyse(qs, 1000, MODELS_1000)
    show(six, "SCALE 1000, six models, all 1,000 questions (left) and entity questions (right)")
    print()
    two = analyse(qs, 4000, MODELS_4000)
    show(two, "SCALE 4000, check against the paper (aya 36.38/31.72, qwen 30.38/31.95)")
    print()
    print("CORRELATION ACROSS THE SIX SCALE-1000 MODELS (exact permutation p over 720 orderings)")
    pairs = [
        ("unaided accuracy (all)", "none", "graph minus retrieval (all)", "gap"),
        ("unaided accuracy (entity)", "unaided_ent", "graph minus retrieval (entity)", "ent_gap"),
        ("unaided accuracy (all)", "none", "absent term", "absent"),
        ("unaided accuracy (entity)", "unaided_ent", "absent term", "absent"),
        ("unaided accuracy (entity)", "unaided_ent", "in-context term", "in_ctx"),
        ("unaided on graph misses", "unaided_gmiss", "absent term", "absent"),
        ("absent term", "absent", "graph minus retrieval (entity)", "ent_gap"),
        ("in-context term", "in_ctx", "graph minus retrieval (entity)", "ent_gap"),
    ]
    spear = lambda a, b: pearson(ranks(a), ranks(b))  # noqa: E731
    for xl, xk, yl, yk in pairs:
        x = [r[xk] for r in six]
        y = [r[yk] for r in six]
        print(f"   {xl:<27} vs {yl:<31} Spearman {spear(x, y):+.2f} (p={perm_p(x, y, spear):.3f})"
              f"   Pearson {pearson(x, y):+.2f} (p={perm_p(x, y, pearson):.3f})")

    d4, d1 = two[0], two[1]
    print(f"\nSCALE 4000, difference between the two models' entity gaps "
          f"{d4['ent_gap'] - d1['ent_gap']:+.2f} = in-context {d4['in_ctx'] - d1['in_ctx']:+.2f}"
          f" + absent {d4['absent'] - d1['absent']:+.2f}")
    for r in six + two:
        print(f"   {r['model']:<20} n={r['n']}  unaided on entity questions {r['unaided_ent']:5.1f}%"
              f"  miss sets: graph {r['n_gmiss']}, retrieval {r['n_rmiss']}")

    fig = ROOT / "paper-aicset-2026" / "figures"
    fig.mkdir(parents=True, exist_ok=True)
    cols = "model scale none graph retr gap unaided_ent in_ctx absent ent_gap unaided_gmiss unaided_rmiss\n"
    with open(fig / "data_six_models.dat", "w", encoding="utf-8", newline="\n") as f:
        f.write(cols)
        for scale, rows in ((1000, six), (4000, two)):
            for r in rows:
                f.write(f"{r['model']} {scale} {r['none']:.2f} {r['graph']:.2f} {r['retr']:.2f} "
                        f"{r['gap']:.2f} {r['unaided_ent']:.2f} {r['in_ctx']:.2f} {r['absent']:.2f} "
                        f"{r['ent_gap']:.2f} {r['unaided_gmiss']:.2f} {r['unaided_rmiss']:.2f}\n")
    print(f"\nwrote {fig / 'data_six_models.dat'}")


if __name__ == "__main__":
    main()
