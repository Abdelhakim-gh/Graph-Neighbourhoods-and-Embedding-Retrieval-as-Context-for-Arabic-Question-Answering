"""Loads Mintaka's full multilingual split files, not the *_ar.json
extracts, which drop questionEntity entirely. Extracts what the
pipeline needs from each row: the Arabic question text (translations.ar),
the QIDs the graph-walk arm starts from (questionEntity), and the gold
answer, which is either one or more entity QIDs with Arabic labels, or a
plain value (numerical/date/boolean/string) with no QID at all.

Schema notes, checked against datasets/mintaka/mintaka_test.json:
questionEntity can carry entityType values other than "entity" (an ordinal
like "first" has entityType "ordinal" and its "name" field is an integer,
not a QID), so a naive read of every questionEntity's "name" as a QID would
be wrong. Non-entity answers store answer.answer as a list of plain values
(int/bool/str), not the {"name", "label"} dicts entity answers use.
"""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class QuestionEntity:
    qid: str
    label_en: str
    mention: str


@dataclass(frozen=True)
class MintakaQuestion:
    id: str
    question_en: str
    question_ar: str
    question_entities: tuple[QuestionEntity, ...]
    answer_type: str  # "entity", "numerical", "date", "boolean", "string"
    answer_qids: tuple[str, ...]        # non-empty only when answer_type == "entity"
    answer_labels_ar: tuple[str, ...]   # Arabic label per QID in answer_qids, same order
    answer_text: str | None             # the plain value, joined, for non-entity answer types
    category: str
    complexity_type: str
    # English label per QID, same order and same length as answer_labels_ar.
    # Only used where the Arabic one is missing; see parse_question.
    answer_labels_en: tuple[str, ...] = ()


def parse_question(row: dict) -> MintakaQuestion:
    # `e["name"] is not None` matters as much as the entityType filter. 41 of
    # the test split's 4,000 rows (1.0%) carry an entity-typed questionEntity
    # whose name is null: Mintaka recorded the mention ("Winston", "Cooke
    # Maroney") but no Wikidata item was linked to it. str(None) would turn
    # those into the string "None", which would then travel as a QID: sent to
    # SPARQL, cached as a "no outgoing edges" sentinel, and counted as a
    # present seed by the coverage check. Dropping them shows those questions
    # with the anchors they really have, and a question with none stays
    # visible as such.
    entities = tuple(
        QuestionEntity(qid=str(e["name"]), label_en=e.get("label", ""), mention=e.get("mention", ""))
        for e in row.get("questionEntity", [])
        if e.get("entityType") == "entity" and e.get("name") is not None
    )

    answer = row["answer"]
    raw_answers = answer.get("answer") or []
    is_entity_answer = answer["answerType"] == "entity"

    answer_qids: tuple[str, ...] = ()
    answer_labels_ar: tuple[str, ...] = ()
    answer_labels_en: tuple[str, ...] = ()
    answer_text = None
    if is_entity_answer:
        answer_qids = tuple(a["name"] for a in raw_answers)
        # `or ""`, not `.get(..., "")`: Mintaka stores an explicit null for a
        # language a gold entity has no label in, so the key is present with
        # value None and a plain default never fires. 7.6% of the test split
        # has at least one such answer, and passing None into the scorer
        # crashes it rather than scoring the item wrong.
        answer_labels_ar = tuple((a.get("label") or {}).get("ar") or "" for a in raw_answers)
        answer_labels_en = tuple((a.get("label") or {}).get("en") or "" for a in raw_answers)
    elif raw_answers:
        answer_text = ", ".join(str(a) for a in raw_answers)

    # 67 of the test split's 4,000 rows (1.7%; 1.5% of train, 0.9% of dev) are
    # answerType "entity" with answer.answer set to null, because Wikidata has
    # no item for the answer. The gold answer is still there, as a free-text
    # string in answer.mention ("Elvis Presto", "George Walton Lucas Sr."). Read
    # only from answer.answer, those rows have no gold string, so
    # answer_correct_entity would match against an empty list and mark every
    # answer wrong.
    if not answer_qids and not answer_text:
        mention = answer.get("mention")
        if mention:
            answer_text = str(mention)

    return MintakaQuestion(
        id=row["id"],
        question_en=row["question"],
        question_ar=row["translations"]["ar"],
        question_entities=entities,
        answer_type=answer["answerType"],
        answer_qids=answer_qids,
        answer_labels_ar=answer_labels_ar,
        answer_text=answer_text,
        category=row["category"],
        complexity_type=row["complexityType"],
        answer_labels_en=answer_labels_en,
    )


def load_split(path: Path) -> list[MintakaQuestion]:
    with open(path, encoding="utf-8") as f:
        rows = json.load(f)
    return [parse_question(r) for r in rows]


def stratified_sample(questions: list[MintakaQuestion], n: int, seed: int = 0) -> list[MintakaQuestion]:
    """A scale tier's N questions, drawn proportionally across
    complexityType x category rather than taken off the top of the file.

    Mintaka's split files are grouped, not shuffled: mintaka_test.json runs
    in 198 contiguous blocks of one complexityType each, and the categories
    are grouped inside those. Taking questions[:N] would sample one corner
    of the file. On mintaka_test.json (4,000 questions, 9 complexity types
    at 10% each bar generic at 20%, 8 categories at 12.5% each):

      first 100 rows:  92% movies, 0% geography, 0% politics, 0%
                       superlative, and exactly 1 multihop question
      first 1000 rows: 0% geography, 0% politics, 0.3% history,
                       0.2% videogames

    Per-category and per-complexity results need every stratum present.

    Proportional allocation with largest-remainder rounding, so the strata
    keep the file's own proportions and the returned list is exactly n long
    (or the whole file, if n exceeds it). seed fixes the shuffle inside each
    stratum, so a tier is reproducible. Rows are returned in the file's
    original order, so a run is deterministic regardless of stratum
    iteration order.

    The tiers nest: the 100-item tier is a strict subset of the 1,000-item
    one (overlap 100/100). This follows from the sampler: one Random(seed)
    is created per call and each stratum is shuffled once, in sorted(strata)
    order, so stratum k gets the same permutation at every n. Proportional
    allocation then gives take_100[k] <= take_1000[k], and each tier takes a
    prefix of that shared permutation. A change in accuracy between tiers is
    then a sample-size effect on nested data, not two independent draws.
    """
    import random

    if n >= len(questions):
        return list(questions)

    strata: dict[tuple[str, str], list[int]] = {}
    for i, q in enumerate(questions):
        strata.setdefault((q.complexity_type, q.category), []).append(i)

    total = len(questions)
    exact = {k: len(v) * n / total for k, v in strata.items()}
    take = {k: int(v) for k, v in exact.items()}
    # largest remainder: hand out the seats integer division dropped
    shortfall = n - sum(take.values())
    for k, _rem in sorted(exact.items(), key=lambda kv: (-(kv[1] - int(kv[1])), kv[0]))[:shortfall]:
        take[k] += 1

    rng = random.Random(seed)
    chosen: list[int] = []
    for key in sorted(strata):
        idxs = list(strata[key])
        rng.shuffle(idxs)
        chosen.extend(idxs[: take[key]])
    return [questions[i] for i in sorted(chosen)]


def select_scale(questions: list[MintakaQuestion], scale: str) -> list[MintakaQuestion]:
    """The one definition of "which questions is scale tier N", shared by
    scripts/01, 02, 03 and 04. Keeping a single definition guarantees that
    every arm runs on the same question set.
    """
    if scale == "all":
        return list(questions)
    return stratified_sample(questions, int(scale))


def collect_qids(questions: list[MintakaQuestion]) -> set[str]:
    """Every QID referenced by this question set: question entities and
    gold answer entities combined. This is the seed set
    scripts/01_collect_qids_and_pull_graph.py pulls a bounded-hop
    neighborhood around.
    """
    qids: set[str] = set()
    for q in questions:
        qids.update(e.qid for e in q.question_entities)
        qids.update(q.answer_qids)
    return qids
