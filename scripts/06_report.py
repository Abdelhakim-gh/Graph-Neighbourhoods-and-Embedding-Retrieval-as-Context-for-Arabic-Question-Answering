"""Turns results/tables/scale_<N>.json into a readable markdown table.
Kept minimal: no charts.

Usage:
    python scripts/06_report.py --scale 100
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES_DIR = ROOT / "results" / "tables"


def fmt_pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def fmt_num(value, spec: str) -> str:
    """Latency and energy are None when a run predates the fields, or when
    pynvml was unavailable on the machine that produced it."""
    return spec.format(value) if value is not None else "n/a"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scale", required=True, help="100, 1000, 10000, or all")
    args = parser.parse_args()

    path = TABLES_DIR / str(args.scale) / f"scale_{args.scale}.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    lines = [
        f"# Study 4 results, scale {args.scale}",
        "",
        "## Overall accuracy, per run (arm|LLM|seed)",
        "",
        "`Truncated` is the share of answers that ended exactly at `max_tokens`.",
        "A high rate means that run was scored on cut-off answers, which is a",
        "pipeline finding rather than a model finding: raise the cap for that",
        "model and re-run it alone. `Errors` are excluded from accuracy rather",
        "than counted wrong.",
        "",
        "| Run | Accuracy | N | Truncated | Errors | Mean s/call | Energy Wh |",
        "|---|---|---|---|---|---|---|",
    ]
    for run_key in sorted(data["runs"]):
        r = data["runs"][run_key]
        mean_s = fmt_num(r.get("mean_wall_clock_s"), "{:.2f}")
        energy = fmt_num(r.get("total_gpu_energy_wh"), "{:.1f}")
        lines.append(
            f"| {run_key}{'' if r.get('complete', True) else ' *(partial)*'} "
            f"| {fmt_pct(r['overall_accuracy'])} | {r['n_items']} "
            f"| {fmt_pct(r.get('truncated_rate', 0.0))} | {r.get('n_errors', 0)} "
            f"| {mean_s} | {energy} |"
        )

    # The arms against each other, with the per-model runs collapsed. This
    # relies on scripts/04 recording the arm as a field; the filename merges
    # arm and model beyond recovery.
    # Runs still being written are kept out of this table, not just flagged.
    # A prefix is a biased sample, because rows follow the file order and
    # `generic` questions (20% of the split) sit at the end.
    # Seeds are averaged within a model before models are averaged across an
    # arm. A flat mean would weight an arm by how many extra seeds its models
    # happen to have: at scale 1,000, two extra seeds of aya-expanse:8b on
    # the graph arm would lift that arm's flat mean from 29.7% to 31.6%.
    by_arm_model: dict[str, dict[str, list[float]]] = {}
    excluded = []
    for run_key, r in data["runs"].items():
        arm = r.get("arm")
        if not arm:
            continue
        label = f"{arm} ({r['embedding_model']})" if r.get("embedding_model") else arm
        if not r.get("complete", True):
            excluded.append((run_key, r["n_items"]))
            continue
        model = r.get("model") or run_key.split("|")[0]
        by_arm_model.setdefault(label, {}).setdefault(model, []).append(r["overall_accuracy"])

    by_arm: dict[str, list[float]] = {
        label: [sum(accs) / len(accs) for accs in models.values()]
        for label, models in by_arm_model.items()
    }
    multi_seed = sorted(
        f"{label}/{model} ({len(accs)} seeds)"
        for label, models in by_arm_model.items()
        for model, accs in models.items()
        if len(accs) > 1
    )

    if by_arm:
        lines += [
            "",
            "## Accuracy per arm, averaged over the LLM roster",
            "",
            "The three-arm comparison this study exists to make. `no_retrieval`",
            "is the control: the gap between it and the other two is what",
            "retrieval and graph-walking actually buy. A gap smaller than about",
            "0.02 should be read as inconclusive rather than as a result, since",
            "this tier runs a single seed at temperature 0.2 and does not",
            "measure its own run-to-run spread.",
            "",
            "| Arm | Mean accuracy | LLMs |",
            "|---|---|---|",
        ]
        for label in sorted(by_arm, key=lambda k: -sum(by_arm[k]) / len(by_arm[k])):
            accs = by_arm[label]
            lines.append(f"| {label} | {fmt_pct(sum(accs) / len(accs))} | {len(accs)} |")

        if multi_seed:
            lines += [
                "",
                f"Seeds averaged within a model before averaging across the arm: "
                f"{', '.join(multi_seed)}. The Runs column counts models, not runs.",
            ]

        if excluded:
            listed = ", ".join(f"{k} ({n} rows)" for k, n in sorted(excluded))
            lines += [
                "",
                f"**{len(excluded)} run(s) still being written are excluded from "
                f"this table:** {listed}. A prefix of this pipeline is a biased "
                f"sample, not a small one, since the questions are not shuffled "
                f"against `complexityType`. Re-run scripts/05 and 06 once the "
                f"file reaches its full row count.",
            ]

        # An arm still being written averages over fewer LLMs than a finished
        # one, and this table sorts by mean accuracy, so a partial arm can
        # take a rank it has not earned. Averages over different rosters are
        # not comparable, so the report says so explicitly.
        counts = {len(v) for v in by_arm.values()}
        if len(counts) > 1:
            widest = max(counts)
            partial = sorted(k for k, v in by_arm.items() if len(v) < widest)
            lines += [
                "",
                f"**Arms cover different rosters, so these means are not directly "
                f"comparable.** {', '.join(partial)} ran on fewer LLMs than the "
                f"{widest} the widest arm covers. Compare per model instead until "
                f"every arm is complete.",
            ]

    lines += [
        "",
        "## Accuracy by answer type, per run",
        "",
        "Where the scorer is weakest, so read a bad number here as a possible",
        "scoring problem before reading it as an arm result: boolean matching is",
        "an Arabic word list, and numerical matching credits an answer whose",
        "*leading* number is the gold value. That numerical rule replaced an",
        "any-number-anywhere one on 2026-08-22, which had been giving the",
        "no-context arm about three times as many chances to be right by",
        "accident, since it hedges and states more numbers per answer.",
        "",
        "| Run | Answer type | Accuracy | N |",
        "|---|---|---|---|",
    ]
    for run_key in sorted(data["runs"]):
        for answer_type, stats in sorted(data["runs"][run_key].get("by_answer_type", {}).items()):
            lines.append(f"| {run_key} | {answer_type} | {fmt_pct(stats['accuracy'])} | {stats['n']} |")

    lines += [
        "",
        "## Accuracy by question complexity type, per run",
        "",
        "This is the study's actual finding: the graph-walk arm is expected to win here on multihop/intersection questions and add nothing on generic/yesno ones.",
        "",
        "| Run | Complexity type | Accuracy | N |",
        "|---|---|---|---|",
    ]
    for run_key in sorted(data["runs"]):
        for complexity_type, stats in sorted(data["runs"][run_key]["by_complexity_type"].items()):
            lines.append(f"| {run_key} | {complexity_type} | {fmt_pct(stats['accuracy'])} | {stats['n']} |")

    lines += ["", "## Accuracy by category, per run", "", "| Run | Category | Accuracy | N |", "|---|---|---|---|"]
    for run_key in sorted(data["runs"]):
        for category, stats in sorted(data["runs"][run_key]["by_category"].items()):
            lines.append(f"| {run_key} | {category} | {fmt_pct(stats['accuracy'])} | {stats['n']} |")

    report = "\n".join(lines) + "\n"
    out_path = TABLES_DIR / str(args.scale) / f"scale_{args.scale}_report.md"
    out_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
