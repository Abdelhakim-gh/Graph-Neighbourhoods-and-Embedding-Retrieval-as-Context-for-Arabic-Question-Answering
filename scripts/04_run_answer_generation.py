"""Answer generation for all three arms, plain retrieval, graph walk, and
the no-retrieval control, sharing one prompt
(prompts/study4_answer_from_context_ar.txt) with an empty {context} for the
control. Resumable via src/common/job_runner.py.

Usage:
    python scripts/04_run_answer_generation.py --scale 100 --arm no_retrieval
    python scripts/04_run_answer_generation.py --scale 100 --arm retrieval --embedding-model bge-m3
    python scripts/04_run_answer_generation.py --scale 100 --arm graph_walk
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATASETS_ROOT = ROOT / "datasets" / "mintaka"
sys.path.insert(0, str(ROOT))

from src.common.job_runner import run_job  # noqa: E402
from src.common.meter import GPUEnergyMeter  # noqa: E402
from src.llm.model_runner import OllamaRunner  # noqa: E402
from src.qa.mintaka_loader import load_split, select_scale  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

PROMPT_PATH = ROOT / "prompts" / "study4_answer_from_context_ar.txt"
SPLIT_FILES = {"train": "mintaka_train.json", "dev": "mintaka_dev.json", "test": "mintaka_test.json"}
RETRIEVAL_DIR = ROOT / "results" / "retrieval"
GRAPH_WALK_DIR = ROOT / "results" / "graph_walk"
RESULTS_DIR = ROOT / "results" / "answers"


def fill_prompt(template: str, context: str, question: str) -> str:
    # str.replace, not str.format, so literal braces in a prompt can never
    # be misparsed.
    return template.replace("{context}", context).replace("{question}", question)


def load_retrieval_context(scale: str, embedding_model: str) -> dict[str, str]:
    safe_name = embedding_model.replace("/", "_").replace(":", "_")
    path = RETRIEVAL_DIR / str(scale) / f"{safe_name}_{scale}.jsonl"
    context_by_item: dict[str, str] = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            sentences = [r["sentence"] for r in row.get("retrieved", [])]
            context_by_item[row["item_id"]] = "\n".join(sentences)
    return context_by_item


def load_built_context(scale: str, name: str) -> dict[str, str]:
    """Contexts written by scripts/11_build_contexts.py:
    results/contexts/{scale}/{name}.jsonl, one row per question with its
    final, already-deduplicated "lines"."""
    path = ROOT / "results" / "contexts" / str(scale) / f"{name}.jsonl"
    with open(path, encoding="utf-8") as f:
        return {row["item_id"]: "\n".join(row["lines"]) for row in map(json.loads, f)}


def load_graph_walk_context(scale: str) -> dict[str, str]:
    path = GRAPH_WALK_DIR / str(scale) / f"walk_{scale}.jsonl"
    context_by_item: dict[str, str] = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            # Order-preserving dedup, needed for arm balance. Sibling paths
            # re-render their shared prefix: A->B->C and A->B->D both emit the
            # "A - rel - B" line, so 28-31% of raw context lines are repeats
            # (measured on walk_100 and walk_1000). top_paths and top_k are
            # matched on distinct lines, so the repeats must be removed.
            seen: set[str] = set()
            sentences = []
            for path_row in row.get("paths", []):
                for s in path_row["sentences"]:
                    if s not in seen:
                        seen.add(s)
                        sentences.append(s)
            context_by_item[row["item_id"]] = "\n".join(sentences)
    return context_by_item


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scale", required=True, help="100, 1000, 10000, or all")
    parser.add_argument("--split", default="test", choices=["train", "dev", "test"])
    parser.add_argument("--arm", required=True, choices=["retrieval", "graph_walk", "no_retrieval", "contexts"])
    parser.add_argument(
        "--context-name", type=str, default=None,
        help="Required for --arm contexts: a file name (without .jsonl) under "
             "results/contexts/{scale}/ written by scripts/11, e.g. scoped_question. "
             "Outputs are tagged ctx_{name}, so they never collide with the original arms.",
    )
    parser.add_argument("--embedding-model", type=str, default=None, help="Required for --arm retrieval: which embedding model's results to use as context")
    parser.add_argument("--models", type=str, default=None, help="Comma-separated LLM model names, default every model in configs/llm_models.yaml")
    parser.add_argument("--seeds", type=str, default=None, help="Comma-separated seeds, default every seed in configs/llm_models.yaml")
    parser.add_argument(
        "--limit", type=int, default=None,
        help="run only the first N questions of the tier. For measuring real per-call "
             "cost and checking hit_token_cap before committing to the full roster; "
             "run_job resumes, so a later full run continues from what this wrote.",
    )
    args = parser.parse_args()

    if args.arm == "retrieval" and not args.embedding_model:
        parser.error("--arm retrieval requires --embedding-model")
    if args.arm == "contexts" and not args.context_name:
        parser.error("--arm contexts requires --context-name")

    with open(ROOT / "configs" / "llm_models.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    prompt_template = PROMPT_PATH.read_text(encoding="utf-8")

    questions = load_split(DATASETS_ROOT / SPLIT_FILES[args.split])
    questions = select_scale(questions, args.scale)
    logger.info("%d questions loaded", len(questions))

    if args.arm == "retrieval":
        context_by_item = load_retrieval_context(args.scale, args.embedding_model)
        arm_tag = f"retrieval_{args.embedding_model.replace('/', '_').replace(':', '_')}"
    elif args.arm == "graph_walk":
        context_by_item = load_graph_walk_context(args.scale)
        arm_tag = "graph_walk"
    elif args.arm == "contexts":
        context_by_item = load_built_context(args.scale, args.context_name)
        arm_tag = f"ctx_{args.context_name}"
    else:
        context_by_item = {}
        arm_tag = "no_retrieval"

    items = [{"item_id": q.id, "question_ar": q.question_ar} for q in questions]
    if args.limit:
        items = items[: args.limit]
        logger.info("--limit %d: running %d of %d questions", args.limit, len(items), len(questions))

    model_names = args.models.split(",") if args.models else [m["name"] for m in cfg["models"]]
    seeds = [int(s) for s in args.seeds.split(",")] if args.seeds else cfg["seeds"]

    (RESULTS_DIR / str(args.scale)).mkdir(parents=True, exist_ok=True)
    meter = GPUEnergyMeter()

    for model_name in model_names:
        runner = OllamaRunner(model_name, host=cfg["ollama_host"], num_ctx=cfg["num_ctx"])
        if not runner.ping():
            logger.error("%s: ping failed (model not pulled, or Ollama not running?), skipping", model_name)
            continue
        safe_name = model_name.replace("/", "_").replace(":", "_")
        for seed in seeds:
            output_path = RESULTS_DIR / str(args.scale) / f"{arm_tag}_{safe_name}_{args.scale}_seed{seed}.jsonl"
            logger.info("%s arm=%s seed=%d scale=%s -> %s", model_name, args.arm, seed, args.scale, output_path)

            def worker(item, seed=seed, runner=runner, model_name=model_name):
                context = context_by_item.get(item["item_id"], "")
                prompt = fill_prompt(prompt_template, context, item["question_ar"])
                with meter.measure() as m:
                    gen = runner.generate(prompt, seed=seed, temperature=cfg["temperature"], max_tokens=cfg["max_tokens"])
                result = m.result()
                return {
                    # Run identity as data rather than parsed back out of the
                    # filename. The filename merges arm, embedding model and
                    # LLM into one string ("retrieval_bge-m3_gemma4_12b"), and
                    # sanitised model names contain underscores, so it cannot
                    # be split apart reliably.
                    "arm": args.arm,
                    "embedding_model": args.embedding_model if args.arm == "retrieval" else None,
                    "context_name": args.context_name if args.arm == "contexts" else None,
                    "model": model_name,
                    "seed": seed,
                    "generated_text": gen.text.strip(),
                    "context_used": context,
                    "tokens_in": gen.tokens_in,
                    "tokens_out": gen.tokens_out,
                    # Recorded per row so truncation is visible directly. A
                    # model with a high rate here was scored on cut-off
                    # answers.
                    "hit_token_cap": gen.hit_token_cap,
                    "wall_clock_s": result.wall_clock_s,
                    "gpu_energy_wh": result.gpu_energy_wh,
                }

            run_job(items, worker, output_path)


if __name__ == "__main__":
    main()
