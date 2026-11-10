"""Walks a pulled Wikidata neighborhood graph from a question's entities,
bounded to max_hops, and ranks the paths found. Settings are in
configs/graph_walk.yaml: max_hops 2 (hop 3 reaches no gold answer the first
two miss) and shortest-then-question-overlap ranking. The
shortest-then-relation-frequency ranking is kept for comparison;
configs/graph_walk.yaml explains why it is not used.

The graph is a plain adjacency list built from (head, relation, tail,
tail_label) triples src/qa/graph_pull.py pulls. Traversal is undirected
(both head->tail and tail->head edges are walkable) since a question can
name a relation from either direction: "who directed X" needs the P57
edge walked backward from X, "what did director Y direct" needs it walked
forward from Y.
"""

import re
from collections import Counter, deque
from dataclasses import dataclass


@dataclass(frozen=True)
class GraphEdge:
    other_qid: str
    relation_pid: str
    direction: str  # "out" (head -> tail) or "in" (tail -> head), from the walk's perspective


@dataclass(frozen=True)
class WalkPath:
    start_qid: str
    target_qid: str
    edges: tuple[GraphEdge, ...]  # in walk order, from start_qid to target_qid

    @property
    def n_hops(self) -> int:
        return len(self.edges)


def build_adjacency(triples: list[tuple[str, str, str, str]]) -> dict[str, list[GraphEdge]]:
    """triples: (head_qid, relation_pid, tail_qid, tail_label), the shape
    src/qa/graph_pull.py::parse_neighborhood_rows returns. Builds both
    directions so the walk below is undirected.
    """
    adjacency: dict[str, list[GraphEdge]] = {}
    for head, rel, tail, _label in triples:
        adjacency.setdefault(head, []).append(GraphEdge(other_qid=tail, relation_pid=rel, direction="out"))
        adjacency.setdefault(tail, []).append(GraphEdge(other_qid=head, relation_pid=rel, direction="in"))
    return adjacency


def find_paths(
    adjacency: dict[str, list[GraphEdge]],
    start_qids: list[str],
    max_hops: int = 3,
) -> dict[str, WalkPath]:
    """Multi-source breadth-first search from every start QID at once,
    bounded to max_hops. Returns {reached_qid: shortest WalkPath to it}, one
    path per reached entity. A tie between two different start QIDs at the
    same hop count keeps whichever was discovered first, which is
    deterministic given a fixed start_qids order.
    """
    visited: dict[str, WalkPath] = {}
    queue: deque[tuple[str, WalkPath]] = deque()
    for start in start_qids:
        if start not in visited:
            visited[start] = WalkPath(start_qid=start, target_qid=start, edges=())
            queue.append((start, visited[start]))

    while queue:
        current_qid, path = queue.popleft()
        if path.n_hops >= max_hops:
            continue
        for edge in adjacency.get(current_qid, []):
            if edge.other_qid in visited:
                continue
            new_path = WalkPath(start_qid=path.start_qid, target_qid=edge.other_qid, edges=path.edges + (edge,))
            visited[edge.other_qid] = new_path
            queue.append((edge.other_qid, new_path))

    return visited


def build_relation_frequency(triples: list[tuple[str, str, str, str]]) -> Counter:
    return Counter(rel for _head, rel, _tail, _label in triples)


def rank_paths_shortest_then_relation_frequency(paths: list[WalkPath], relation_frequency: Counter) -> list[WalkPath]:
    """Baseline ranking, kept for comparison and not used by the pipeline.

    Sorts by hop count first, then by the summed corpus frequency of the
    path's relations, most frequent first. The most frequent relations in a
    Wikidata neighborhood are taxonomy and biographical boilerplate, P31
    (instance of) and P106 (occupation), which took 63% of the top-5 slots
    across 60 scale-100 questions and almost never lead to the answer. At
    top 5 this ranking puts the gold answer in context 0.0% of the time.
    """

    def relation_score(path: WalkPath) -> int:
        return sum(relation_frequency.get(e.relation_pid, 0) for e in path.edges)

    return sorted(paths, key=lambda p: (p.n_hops, -relation_score(p)))


def _content_words(text: str) -> set[str]:
    """Words worth matching on, from an Arabic question or a rendered label.
    Splits on whitespace and both Arabic and Latin punctuation, then drops
    tokens of 2 characters or fewer, which in Arabic are overwhelmingly
    particles and prepositions (من, في, ما) that match everything and
    separate nothing.
    """
    return {t for t in re.split(r"[\s،.,؟?!()\[\]\"'\-:؛]+", text) if len(t) > 2}


def rank_paths_shortest_then_question_overlap(
    paths: list[WalkPath],
    question_ar: str,
    entity_labels: dict[str, str],
    relation_labels: dict[str, str],
    relation_frequency: Counter | None = None,
) -> list[WalkPath]:
    """configs/graph_walk.yaml's path_ranking:
    "shortest_then_question_overlap". Sorts by hop count first, then by how
    many content words the path's own rendered labels share with the Arabic
    question, most shared first, then by rarest relation as a final
    tiebreak when relation_frequency is supplied.

    A walk from a question entity reaches tens of thousands of nodes (median
    14,351 within 2 hops on the scale-100 pull), and hop count alone cannot
    separate the few the question is about. The question text is the only
    signal specific to this question, and matching against it needs no model
    call, so scripts/03 stays a pure traversal.

    The match is lexical, not semantic, so it misses paraphrases. When
    overlap is zero for every candidate, which is common for deeper paths,
    the rarest-relation tiebreak decides. The semantic version of this term
    is the retrieval arm itself, so using an embedding model here would blur
    the comparison.
    """

    def relation_score(path: WalkPath) -> int:
        if relation_frequency is None:
            return 0
        return sum(relation_frequency.get(e.relation_pid, 0) for e in path.edges)

    question_words = _content_words(question_ar)

    def overlap(path: WalkPath) -> int:
        words = _content_words(entity_labels.get(path.target_qid, ""))
        for edge in path.edges:
            words |= _content_words(relation_labels.get(edge.relation_pid, ""))
            words |= _content_words(entity_labels.get(edge.other_qid, ""))
        return len(question_words & words)

    return sorted(paths, key=lambda p: (p.n_hops, -overlap(p), relation_score(p)))


def path_to_sentences(path: WalkPath, entity_labels: dict[str, str], relation_labels: dict[str, str]) -> list[str]:
    """Renders a WalkPath as one "X - relation - Y" line per hop, in the
    direction the fact was actually stated (an "in" edge, walked backward,
    is flipped back to head-relation-tail order rather than printed
    backward), for the answer-generation prompt. Same flat format as
    src/qa/retrieval.py::triple_to_sentence, kept separate because this one
    tracks the walk's current position hop by hop.

    A QID with no known label falls back to printing the bare QID rather
    than raising, since a caller building context for one path should not
    lose the whole path over a single missing label.
    """
    sentences = []
    current = path.start_qid
    for edge in path.edges:
        # `or <qid/pid>` rather than a plain default: an empty-string label
        # is how ensure_property_labels records "asked Wikidata, no Arabic
        # label exists", and a blank gap mid-sentence is worse than the ID.
        head_label = entity_labels.get(current) or current
        tail_label = entity_labels.get(edge.other_qid) or edge.other_qid
        relation_label = relation_labels.get(edge.relation_pid) or edge.relation_pid
        if edge.direction == "out":
            sentences.append(f"{head_label} - {relation_label} - {tail_label}")
        else:
            sentences.append(f"{tail_label} - {relation_label} - {head_label}")
        current = edge.other_qid
    return sentences


def reached_target(paths: dict[str, WalkPath], target_qids: tuple[str, ...]) -> WalkPath | None:
    """Returns the shortest path to any of target_qids that the walk
    reached, or None if none were reached within max_hops. Used both for
    evaluation (did the walk reach the gold answer) and, at real inference
    time with an unknown answer, for checking whether a candidate the
    answer-generation model proposes is actually graph-connected.
    """
    reached = [paths[qid] for qid in target_qids if qid in paths]
    if not reached:
        return None
    return min(reached, key=lambda p: p.n_hops)
