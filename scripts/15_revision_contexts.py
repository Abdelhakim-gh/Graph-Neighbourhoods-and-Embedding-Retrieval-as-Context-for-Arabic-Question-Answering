"""Context files for the revision runs (50-line budget, question-only store,
one-hop walk).

Every new run uses the 1,000 stratified questions of the six-model tier
(select_scale(..., "1000")), which are a subset of the 4,000 already answered.
Each new run is therefore paired, question by question, with the existing
4,000-question run on the same questions; no 150-line gold-store run is
repeated.

Writes results/contexts/1000/<name>.jsonl, one row per question,
{"item_id", "lines"}, in the format scripts/04 reads with --arm contexts.

  budget   walk_answered_k50, pooled_answered_k50: the first 50 lines of the
           exact contexts the 4,000-question graph and pooled runs used
           (walk_4000.jsonl with scripts/04's order-preserving dedup;
           the E5 retrieval file, already sorted by score).
  subset   any results/contexts/4000/<name>.jsonl written by scripts/11
           (walk_question, pooled_question, scoped_question,
           walk_answered_h1, ...), cut to the 1,000 questions.

Usage:
  py -3.14 scripts/15_revision_contexts.py budget --k 50
  py -3.14 scripts/15_revision_contexts.py subset --names walk_question pooled_question
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.qa.mintaka_loader import load_split, select_scale  # noqa: E402

OUT = ROOT / "results" / "contexts" / "1000"


def tier_ids():
    qs = select_scale(load_split(ROOT / "datasets" / "mintaka" / "mintaka_test.json"), "1000")
    return [q.id for q in qs]


def dedup(lines):
    seen, out = set(), []
    for s in lines:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def archived_walk():
    out = {}
    for line in open(ROOT / "results" / "graph_walk" / "4000" / "walk_4000.jsonl", encoding="utf-8"):
        row = json.loads(line)
        out[row["item_id"]] = dedup(s for p in row.get("paths", []) for s in p["sentences"])
    return out


def archived_pooled():
    out = {}
    path = ROOT / "results" / "retrieval" / "4000" / "intfloat_multilingual-e5-large_4000.jsonl"
    for line in open(path, encoding="utf-8"):
        row = json.loads(line)
        scores = [r["score"] for r in row["retrieved"]]
        assert scores == sorted(scores, reverse=True), row["item_id"]
        # scripts/04's load_retrieval_context joins the sentences as they are,
        # so the 150-line run saw repeats too; keep the same order and take the
        # first k distinct lines, which is what a 50-line budget would show.
        out[row["item_id"]] = dedup(r["sentence"] for r in row["retrieved"])
    return out


def write(name, ids, ctx):
    OUT.mkdir(parents=True, exist_ok=True)
    missing = [i for i in ids if i not in ctx]
    if missing:
        raise SystemExit(f"{name}: {len(missing)} questions missing from the source")
    path = OUT / f"{name}.jsonl"
    if path.exists():
        raise SystemExit(f"{path} exists; delete it first if it is meant to be rebuilt")
    with open(path.with_suffix(".tmp"), "w", encoding="utf-8") as f:
        for i in ids:
            f.write(json.dumps({"item_id": i, "lines": ctx[i]}, ensure_ascii=False) + "\n")
    path.with_suffix(".tmp").replace(path)
    lens = sorted(len(ctx[i]) for i in ids)
    print(f"wrote {path.relative_to(ROOT)}: {len(ids)} questions, lines median {lens[len(lens) // 2]}, "
          f"max {lens[-1]}, empty {sum(1 for x in lens if x == 0)}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("budget")
    b.add_argument("--k", type=int, required=True)
    s = sub.add_parser("subset")
    s.add_argument("--names", nargs="+", required=True)
    args = ap.parse_args()
    ids = tier_ids()
    assert len(ids) == len(set(ids)) == 1000
    if args.cmd == "budget":
        for name, src in (("walk_answered", archived_walk()), ("pooled_answered", archived_pooled())):
            write(f"{name}_k{args.k}", ids, {i: v[: args.k] for i, v in src.items()})
    else:
        for name in args.names:
            rows = {r["item_id"]: r["lines"] for r in
                    map(json.loads, open(ROOT / "results" / "contexts" / "4000" / f"{name}.jsonl", encoding="utf-8"))}
            write(name, ids, rows)


if __name__ == "__main__":
    main()
