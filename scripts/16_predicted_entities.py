"""Predict question entities, link them to Wikidata, and build walk contexts.

Commands use the stratified 1,000-question test tier. Limit runs use separate
files and are for testing only. Metrics exclude questions without gold QIDs
from gold-coverage denominators; no-prediction uses all questions.
"""
import argparse
from collections import defaultdict
import json
import logging
import re
import sys
import time
from importlib import import_module
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
from src.qa.graph_pull import (_client, cap_triples_per_head, drop_excluded_properties,
                               expand_neighborhood, fetch_neighborhood, fetch_property_labels, scope_to_seeds)
from src.qa.graph_walk import (build_adjacency, build_relation_frequency, find_paths,
                               path_to_sentences, rank_paths_shortest_then_question_overlap)
from src.qa.mintaka_loader import load_split, select_scale

LOG = logging.getLogger(__name__)
AGENT = "Study4-AICSET-research/1.0 (https://github.com/Abdelhakim-gh; academic research script)"
MAIN_CACHE = ROOT / "data/processed/graph_cache/triples.jsonl"
LINK_CACHE = ROOT / "data/processed/linking/wbsearch_cache.jsonl"
QID = re.compile(r"Q[1-9][0-9]*\Z")


def suffix(limit):
    return f"_limit{limit}" if limit is not None else ""


def result_path(name, limit, folder="linking", ext="jsonl"):
    return ROOT / "results" / folder / "1000" / f"{name}{suffix(limit)}.{ext}"


def linked_cache(limit):
    return ROOT / "data/processed/graph_cache_linked" / f"triples{suffix(limit)}.jsonl"


def rows(path):
    if not path.exists():
        raise FileNotFoundError(f"Required input missing: {path}")
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_rows(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for row in data:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    tmp.replace(path)


def parse_mentions(raw, question=None):
    """Return (mentions, parsed). Only complete arrays of strings are valid."""
    decoder = json.JSONDecoder()
    try:
        obj, _ = decoder.raw_decode(raw.lstrip())
        if not isinstance(obj, list):
            return [], False
    except json.JSONDecodeError:
        pass
    for match in re.finditer(r"\[", raw):
        try:
            obj, _ = decoder.raw_decode(raw[match.start():])
        except json.JSONDecodeError:
            continue
        if isinstance(obj, list) and all(isinstance(x, str) for x in obj):
            mentions = [x for x in obj if x and (question is None or x in question)]
            return list(dict.fromkeys(mentions)), True
        return [], False
    return [], False


def mentions_command(questions, limit):
    from src.llm.model_runner import OllamaRunner
    path = result_path("mentions_aya-expanse_8b", limit)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = rows(path) if path.exists() else []
    done = {r["item_id"] for r in existing}
    prompt = (ROOT / "prompts" / "study4_entity_mentions_ar.txt").read_text(encoding="utf-8")
    runner = OllamaRunner("aya-expanse:8b", num_ctx=8192)
    with path.open("a", encoding="utf-8") as f:
        for q in questions:
            if q.id in done:
                continue
            result = runner.generate(prompt.format(question=q.question_ar), seed=1, temperature=0, max_tokens=128)
            found, parsed = parse_mentions(result.text, q.question_ar)
            row = {"item_id": q.id, "mentions": found, "raw_output": result.text,
                   "parsed": parsed, "hit_token_cap": result.hit_token_cap}
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            existing.append(row)
    LOG.info("mentions: %d rows, %d unparseable", len(existing), sum(not r["parsed"] for r in existing))


class SearchCache:
    def __init__(self, path=LINK_CACHE):
        self.path = path
        self.cache = {r["search"]: r["response"] for r in rows(path)} if path.exists() else {}
        self.last_request = 0.0

    def search(self, term):
        if term in self.cache:
            return self.cache[term]
        params = {"action": "wbsearchentities", "search": term, "language": "ar", "uselang": "ar",
                  "type": "item", "limit": 5, "format": "json", "maxlag": 5}
        req = Request("https://www.wikidata.org/w/api.php?" + urlencode(params), headers={"User-Agent": AGENT})
        # Wikidata can answer 429 after sustained use (here after about 30
        # calls): honour Retry-After, wait at least a minute, retry up to 12
        # times, and keep to one call per second.
        for attempt in range(12):
            time.sleep(max(0, 1.0 - (time.monotonic() - self.last_request)))
            self.last_request = time.monotonic()
            try:
                with urlopen(req, timeout=30) as response:
                    data = json.load(response)
                if "error" in data:
                    if data["error"].get("code") == "maxlag":
                        raise RuntimeError("maxlag")
                    raise ValueError(f"Wikidata API error: {data['error']}")
                if not isinstance(data.get("search"), list):
                    raise ValueError("Wikidata response has no search list")
                self.path.parent.mkdir(parents=True, exist_ok=True)
                with self.path.open("a", encoding="utf-8") as f:
                    f.write(json.dumps({"search": term, "response": data}, ensure_ascii=False) + "\n")
                self.cache[term] = data
                return data
            except HTTPError as exc:
                if exc.code != 429 and not 500 <= exc.code < 600:
                    raise
                error = exc
                if exc.code == 429:
                    retry_after = exc.headers.get("Retry-After", "")
                    wait = int(retry_after) if retry_after.isdigit() else 60
                    LOG.warning("429 from Wikidata; waiting %d s", max(wait, 60))
                    time.sleep(max(wait, 60))
                    continue
            except (URLError, TimeoutError, RuntimeError) as exc:
                error = exc
            if attempt == 11:
                raise RuntimeError(f"Search failed for {term!r}") from error
            time.sleep(min(2 ** attempt, 30))
        raise RuntimeError(f"Search failed for {term!r} after 12 attempts") from error


def link_mentions(mentions, search):
    candidates, predicted = [], []
    for mention in mentions:
        terms = [mention]
        responses = [search(mention)]
        if not responses[0]["search"] and mention.startswith("ال") and len(mention) > 2:
            terms.append(mention[2:])
            responses.append(search(terms[-1]))
        hits = responses[-1]["search"]
        if hits and QID.fullmatch(hits[0].get("id", "")):
            predicted.append(hits[0]["id"])
        candidates.append({"mention": mention, "searches": [
            {"search": term, "candidates": response["search"]} for term, response in zip(terms, responses)]})
    return list(dict.fromkeys(predicted)), candidates


def checked_rows(questions, path):
    indexed = {r["item_id"]: r for r in rows(path)}
    missing = [q.id for q in questions if q.id not in indexed]
    if missing:
        raise ValueError(f"{path} is missing {len(missing)} required items")
    return indexed


def link_command(questions, limit):
    inputs = checked_rows(questions, result_path("mentions_aya-expanse_8b", limit))
    cache = SearchCache()
    out = []
    for q in questions:
        m = inputs[q.id]["mentions"]
        predicted, candidates = link_mentions(m, cache.search)
        out.append({"item_id": q.id, "mentions": m, "predicted_qids": predicted, "candidates": candidates})
    write_rows(result_path("links", limit), out)


def gold_qids(q):
    return {e.qid for e in q.question_entities if QID.fullmatch(e.qid)}


def metrics(questions, links):
    tp = predictions = gold_count = eligible = all_found = any_found = none_found = no_prediction = 0
    for q in questions:
        gold = gold_qids(q)
        pred = set(links[q.id]["predicted_qids"])
        hit = gold & pred
        tp += len(hit)
        predictions += len(pred)
        gold_count += len(gold)
        no_prediction += not pred
        if gold:
            eligible += 1
            all_found += gold <= pred
            any_found += bool(hit)
            none_found += not hit
    ratio = lambda a, b: a / b if b else None
    return {"questions": len(questions), "questions_with_gold": eligible, "true_positive_qids": tp,
            "predicted_qids": predictions, "gold_qids": gold_count,
            "micro_precision": ratio(tp, predictions), "micro_recall": ratio(tp, gold_count),
            "all_gold_found": ratio(all_found, eligible), "at_least_one_gold_found": ratio(any_found, eligible),
            "no_gold_found": ratio(none_found, eligible), "no_prediction": ratio(no_prediction, len(questions)),
            "questions_without_gold": len(questions) - eligible}


def evaluate_command(questions, limit):
    links = checked_rows(questions, result_path("links", limit))
    groups = defaultdict(list)
    for q in questions:
        groups[q.complexity_type].append(q)
    report = {"overall": metrics(questions, links), "by_complexityType": {
        key: metrics(group, links) for key, group in sorted(groups.items())},
        "denominators": "Gold coverage shares exclude questions without gold QIDs; no_prediction uses all questions."}
    path = result_path("entity_linking_1000", limit, "tables", "json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["overall"], ensure_ascii=False, indent=2))


def pull_command(questions, limit, cfg):
    links = checked_rows(questions, result_path("links", limit))
    seeds = {qid for q in questions for qid in links[q.id]["predicted_qids"]}
    pull = import_module("01_collect_qids_and_pull_graph")
    dest = linked_cache(limit)
    caches = [MAIN_CACHE, dest]
    # Limit runs can reuse the production linked cache without modifying it.
    if limit is not None:
        caches.insert(1, linked_cache(None))
    heads, by_head = set(), defaultdict(list)
    for path in caches:
        heads.update(pull.load_cached_heads(path))
        for head, triples in pull.load_cached_triples_by_head(path).items():
            by_head[head].extend(triples)
    sparql = _client("https://query.wikidata.org/sparql", AGENT)
    dest.parent.mkdir(parents=True, exist_ok=True)

    def fetch(qids):
        fetched, failures = [], set()
        for offset in range(0, len(qids), 25):
            batch = qids[offset:offset + 25]
            triples, failed = fetch_neighborhood(sparql, batch)
            triples = cap_triples_per_head(triples, cfg["max_neighbors_per_qid"])
            with dest.open("a", encoding="utf-8") as f:
                for h, r, t, label in triples:
                    f.write(json.dumps({"head": h, "relation": r, "tail": t, "tail_label": label}, ensure_ascii=False) + "\n")
                for h in sorted(set(batch) - failed - {t[0] for t in triples}):
                    f.write(json.dumps({"head": h, "relation": None, "tail": None, "tail_label": None}) + "\n")
            fetched.extend(triples)
            failures.update(failed)
        return fetched, failures

    triples, queried = expand_neighborhood(fetch, seeds, heads, by_head, cfg["max_hops"], cfg["max_neighbors_per_qid"])
    LOG.info("pulled %d triples for %d heads", len(triples), len(queried))


def build_seeds(all_questions, tier_ids, links):
    return {qid for q in all_questions for qid in (
        links.get(q.id, {}).get("predicted_qids", []) if q.id in tier_ids
        else [e.qid for e in q.question_entities if QID.fullmatch(e.qid)])}


def contexts_command(all_questions, tier, run_questions, limit, cfg):
    links = checked_rows(run_questions, result_path("links", limit))
    if limit is not None and result_path("links", None).exists():
        full = {r["item_id"]: r for r in rows(result_path("links", None))}
        full.update(links)
        links = full
    missing = len(tier) - sum(q.id in links for q in tier)
    if missing:
        if limit is None:
            raise ValueError(f"Missing predictions for {missing} tier questions")
        LOG.warning("Limit run: %d other tier questions have no predictions in the store", missing)
    retrieval = import_module("02_run_retrieval")
    triples = retrieval.load_cached_triples(MAIN_CACHE)
    for cache in dict.fromkeys([linked_cache(None), linked_cache(limit)]):
        if cache.exists():
            triples += retrieval.load_cached_triples(cache)
    triples = drop_excluded_properties(triples, cfg.get("excluded_properties"))
    seeds = build_seeds(all_questions, {q.id for q in tier}, links)
    store = scope_to_seeds(triples, seeds, cfg["max_hops"])
    labels = retrieval.build_head_labels(all_questions, triples)
    for row in links.values():
        for entry in row["candidates"]:
            for search in entry["searches"]:
                for candidate in search["candidates"]:
                    if candidate.get("id") and candidate.get("label"):
                        labels.setdefault(candidate["id"], candidate["label"])
    # Seed the separate label file from the main one, without modifying it.
    label_path = ROOT / "data/processed/graph_cache_linked" / f"property_labels{suffix(limit)}.json"
    label_path.parent.mkdir(parents=True, exist_ok=True)
    main_labels = retrieval.PROPERTY_LABELS_PATH
    if not label_path.exists() and main_labels.exists():
        label_path.write_bytes(main_labels.read_bytes())
    relation_labels = json.loads(label_path.read_text(encoding="utf-8")) if label_path.exists() else {}
    wanted = {t[1] for t in store}
    missing_labels = sorted(wanted - relation_labels.keys())
    sparql = None
    if missing_labels:
        sparql = _client("https://query.wikidata.org/sparql", AGENT)
        arabic = fetch_property_labels(sparql, missing_labels)
        relation_labels.update({pid: arabic.get(pid, "") for pid in missing_labels})
    blank = sorted(pid for pid in wanted if not relation_labels.get(pid))
    if blank:
        sparql = sparql or _client("https://query.wikidata.org/sparql", AGENT)
        relation_labels.update({pid: label for pid, label in
                                fetch_property_labels(sparql, blank, labels_language="en").items() if label})
    if missing_labels or blank:
        label_path.write_text(json.dumps(relation_labels, ensure_ascii=False, indent=1), encoding="utf-8")
    adjacency = build_adjacency(store)
    frequency = build_relation_frequency(store)
    output = []
    for q in run_questions:
        starts = links[q.id]["predicted_qids"]
        paths = find_paths(adjacency, starts, max_hops=cfg["max_hops"]) if starts else {}
        candidates = [p for p in paths.values() if p.n_hops > 0]
        ranked = rank_paths_shortest_then_question_overlap(candidates, q.question_ar, labels, relation_labels, frequency)[:cfg["top_paths"]]
        lines = list(dict.fromkeys(s for p in ranked for s in path_to_sentences(p, labels, relation_labels)))
        output.append({"item_id": q.id, "lines": lines, "pool_size": len(candidates), "starts": starts})
    write_rows(result_path("walk_predicted", limit, "contexts"), output)
    lengths = sorted(len(r["lines"]) for r in output)
    LOG.info("contexts: %d questions, median lines %d, empty %d", len(output),
             lengths[len(lengths) // 2] if lengths else 0, sum(x == 0 for x in lengths))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["mentions", "link", "evaluate", "pull", "contexts"])
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    if args.limit is not None and not 1 <= args.limit <= 1000:
        parser.error("--limit must be between 1 and 1000")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    all_questions = load_split(ROOT / "datasets/mintaka/mintaka_test.json")
    tier = select_scale(all_questions, "1000")
    selected = tier[:args.limit] if args.limit is not None else tier
    if args.command == "mentions":
        mentions_command(selected, args.limit)
    elif args.command == "link":
        link_command(selected, args.limit)
    elif args.command == "evaluate":
        evaluate_command(selected, args.limit)
    else:
        cfg = yaml.safe_load((ROOT / "configs/graph_walk.yaml").read_text(encoding="utf-8"))
        if args.command == "pull":
            pull_command(selected, args.limit, cfg)
        else:
            contexts_command(all_questions, tier, selected, args.limit, cfg)


if __name__ == "__main__":
    main()
