"""Turns pulled graph triples into retrievable sentences and ranks them
against a question by cosine similarity, for the plain-retrieval arm. The
embedding call
itself (turning text into a vector) is isolated to a thin adapter passed in
by the caller; everything here is pure numeric ranking over already-computed
vectors, so it is unit-tested without loading any embedding model.
"""

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievableFact:
    head_qid: str
    relation_pid: str
    tail_qid: str
    sentence: str  # the fact rendered as one line of text, what gets embedded and shown to the answer LLM


def triple_to_sentence(head_label: str, relation_label: str, tail_label: str) -> str:
    """A flat "X - relation - Y" line, not a grammatical sentence. Local
    models handle structured fact lines well, and grammatical Arabic would
    need a template per relation, which an open-ended relation set does not
    have.
    """
    return f"{head_label} - {relation_label} - {tail_label}"


def build_retrievable_facts(
    triples: list[tuple[str, str, str, str]],  # (head_qid, relation_pid, tail_qid, tail_label)
    head_labels: dict[str, str],
    relation_labels: dict[str, str],
) -> list[RetrievableFact]:
    """head_labels and relation_labels are qid/pid -> label lookups the
    caller already has (from the pulled graph and Wikidata property
    labels); a triple whose head has no known label is skipped rather than
    rendered with a bare QID, since a QID is not something an embedding
    model or the answer LLM can make sense of.
    """
    facts = []
    for head, rel, tail, tail_label in triples:
        head_label = head_labels.get(head)
        # `or rel`, not a plain default: ensure_property_labels records a
        # property Wikidata has no Arabic label for as an empty string, so
        # it is not re-queried every run. That must render as the PID, not
        # as a blank gap in the middle of the sentence.
        relation_label = relation_labels.get(rel) or rel
        if head_label is None:
            continue
        sentence = triple_to_sentence(head_label, relation_label, tail_label)
        facts.append(RetrievableFact(head_qid=head, relation_pid=rel, tail_qid=tail, sentence=sentence))
    return facts


def build_literal_facts(
    literals: list[tuple[str, str, str]],  # (head_qid, relation_pid, value)
    head_labels: dict[str, str],
    relation_labels: dict[str, str],
) -> list[RetrievableFact]:
    """Date and quantity claims as retrievable sentences, in the same
    "X - relation - Y" shape as entity facts so the answer LLM sees one
    consistent context format rather than two.

    tail_qid is empty: these facts have no tail entity, so nothing
    downstream can turn them into a walkable edge. The graph-walk arm builds
    its adjacency from triples.jsonl, which never contains them (scripts/01
    writes literals to a separate file). The retrieval corpus needs dates
    and numbers; the walk does not, and a date shared by thousands of
    entities would become a large hub node.
    """
    facts = []
    for head, rel, value in literals:
        head_label = head_labels.get(head)
        if head_label is None:
            continue
        # `or rel`, not a plain default: ensure_property_labels records a
        # property Wikidata has no Arabic label for as an empty string, so
        # it is not re-queried every run. That must render as the PID, not
        # as a blank gap in the middle of the sentence.
        relation_label = relation_labels.get(rel) or rel
        facts.append(
            RetrievableFact(
                head_qid=head,
                relation_pid=rel,
                tail_qid="",
                sentence=triple_to_sentence(head_label, relation_label, value),
            )
        )
    return facts


def retrieval_hit(
    retrieved: list[dict],
    answer_type: str,
    answer_qids: tuple[str, ...],
    answer_text: str | None,
) -> bool | None:
    """Does the retrieved set contain a fact naming the gold answer?

    A metric separate from final-answer accuracy, used to choose which two
    of the seven embedding models go through answer generation. It needs no
    model call, so the embedding comparison is settled before any LLM runs.

    Returns None, not False, where the question is not meaningful. A yes or
    no cannot appear in a retrieved Wikidata fact, so counting boolean
    questions as misses would lower every model's hit rate by the share of
    boolean questions in the tier. Callers aggregate over the non-None ones.

    Entity answers match on QID rather than on label text, in either
    position: a fact is a hit whether the gold entity is its subject or
    its object, since "Mark Twain - occupation - author" names Mark Twain
    just as much as "Tom Sawyer - author - Mark Twain" does.
    """
    if answer_type == "boolean":
        return None

    if answer_type == "entity":
        if not answer_qids:
            return None
        gold = set(answer_qids)
        return any(r.get("head_qid") in gold or r.get("tail_qid") in gold for r in retrieved)

    if not answer_text:
        return None

    if answer_type in ("numerical", "date"):
        from src.qa.qa_scorer import extract_numbers

        gold_numbers = extract_numbers(answer_text)
        if not gold_numbers:
            return None
        joined = " ".join(r.get("sentence", "") for r in retrieved)
        return bool(gold_numbers & extract_numbers(joined))

    return any(answer_text in r.get("sentence", "") for r in retrieved)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def normalize_matrix(fact_embeddings):
    """L2-normalises the corpus once, so each question costs one matrix
    product instead of a Python loop over every fact.

    top_k_by_similarity below recomputes both vector norms for every
    (question, fact) pair in pure Python. That is fine for the unit tests
    and far too slow at real scale: 75,000 facts x 100 questions x 1,024
    dimensions is about eight billion float operations per embedding model
    at the 100-question tier. Returns a numpy array; the import is local so
    the pure-Python path above stays dependency-free for the tests.
    """
    import numpy as np

    matrix = np.asarray(fact_embeddings, dtype=np.float32)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0  # a zero vector scores 0 against everything, not NaN
    return matrix / norms


def top_k_by_similarity_matrix(
    query_embedding: list[float],
    facts: list[RetrievableFact],
    normalized_facts,
    k: int,
) -> list[tuple[RetrievableFact, float]]:
    """Vectorised equivalent of top_k_by_similarity, taking the matrix
    normalize_matrix already prepared. Same return shape and same ordering.
    """
    import numpy as np

    query = np.asarray(query_embedding, dtype=np.float32)
    norm = float(np.linalg.norm(query))
    if norm == 0:
        return [(fact, 0.0) for fact in facts[:k]]

    scores = normalized_facts @ (query / norm)
    k = min(k, len(facts))
    top = np.argpartition(-scores, k - 1)[:k] if k < len(facts) else np.arange(len(facts))
    top = top[np.argsort(-scores[top])]
    return [(facts[i], float(scores[i])) for i in top]


def top_k_by_similarity(
    query_embedding: list[float],
    facts: list[RetrievableFact],
    fact_embeddings: list[list[float]],
    k: int,
) -> list[tuple[RetrievableFact, float]]:
    """facts and fact_embeddings are parallel lists (fact_embeddings[i] is
    the embedding of facts[i].sentence), kept separate rather than bundled
    into RetrievableFact itself so RetrievableFact stays a plain,
    JSON-serialisable record independent of which embedding model produced
    a given vector.
    """
    if len(facts) != len(fact_embeddings):
        raise ValueError(f"facts and fact_embeddings must be parallel lists, got {len(facts)} and {len(fact_embeddings)}")
    scored = [(fact, cosine_similarity(query_embedding, emb)) for fact, emb in zip(facts, fact_embeddings)]
    scored.sort(key=lambda pair: -pair[1])
    return scored[:k]
