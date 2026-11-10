"""Scores a generated Arabic answer against Mintaka's gold answer, and
aggregates accuracy by complexityType and category, since the graph-walk
arm is expected to help most on multihop and intersection questions.

Entity answers: exact match after Arabic normalisation, with a rapidfuzz
fallback for near-miss phrasing.

Non-entity answers (45 of the scale-100 tier's 100 questions):

- boolean: an Arabic yes/no word list, not a general NLU judgement. A
  generated answer that commits to neither scores as incorrect, since a
  model that will not commit has not answered. Refusals are separated from
  "no": "لا أعرف" (I do not know) opens with the no-word and would
  otherwise score as a definite "no".
- numerical: the number the generated text *leads with* has to be the gold
  value, after folding Arabic-Indic digits to ASCII and mapping spelled-out
  numbers up to ten. So "1 جائزة", "الجواب: 1" and
  "تم ترشيحه لجائزة أوسكار واحدة" all score correct against gold "1",
  while an answer that reaches the gold number only in a later clause does
  not. Imperial-height golds (5'7") and multi-value golds get their own
  rules; see answer_correct_numerical.
- date: same digit folding, plus Arabic month names, then a match requires
  every component of the gold date to appear. A year alone against a
  full gold date stays incorrect on purpose.
- string: normalised-string fuzzy match.
"""

import re
from collections import defaultdict
from dataclasses import dataclass

import pyarabic.araby as araby
from rapidfuzz import fuzz

DEFAULT_FUZZY_THRESHOLD = 90.0

_YES_WORDS = ("نعم", "أجل", "صحيح", "yes", "true")
_NO_WORDS = ("لا", "كلا", "ليس", "غير صحيح", "no", "false")

# Checked before the no-word list, because each of these opens with one.
# A refusal is not an answer of "no": scoring it as one credits the model
# for a coin flip on every boolean question it declines.
_REFUSALS = (
    "لا أعرف", "لا اعرف", "لا أستطيع", "لا استطيع", "لست متأكدا", "غير معروف",
    # The more common phrasing when the context lacks the answer: "there is no
    # information in the provided text". These also open with the no-word.
    # Mintaka's boolean gold skews toward "no" (9 of the 15 boolean questions
    # at scale 100), so scoring such a refusal as "no" would bias boolean
    # accuracy upward.
    "لا توجد معلومات", "لا يوجد معلومات", "لا معلومات", "لا تتوفر",
    "غير مذكور", "لم يذكر", "لا يمكن تحديد", "لا يمكن استنتاج",
)

_ARABIC_INDIC = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")

# Mintaka's count answers are small, so spelling them out is a realistic
# model output. Both the masculine and feminine forms, since the gendered
# form follows the counted noun ("جائزة واحدة", "فيلم واحد").
_SPELLED_NUMBERS = {
    "صفر": 0, "واحد": 1, "واحدة": 1, "اثنان": 2, "اثنين": 2, "اثنتان": 2, "اثنتين": 2,
    "ثلاثة": 3, "ثلاث": 3, "أربعة": 4, "أربع": 4, "خمسة": 5, "خمس": 5,
    "ستة": 6, "ست": 6, "سبعة": 7, "سبع": 7, "ثمانية": 8, "ثماني": 8,
    "تسعة": 9, "تسع": 9, "عشرة": 10, "عشر": 10,
}

_ARABIC_MONTHS = {
    "يناير": 1, "كانون الثاني": 1, "فبراير": 2, "شباط": 2, "مارس": 3, "آذار": 3,
    "أبريل": 4, "نيسان": 4, "مايو": 5, "أيار": 5, "يونيو": 6, "حزيران": 6,
    "يوليو": 7, "تموز": 7, "أغسطس": 8, "آب": 8, "سبتمبر": 9, "أيلول": 9,
    "أكتوبر": 10, "تشرين الأول": 10, "نوفمبر": 11, "تشرين الثاني": 11,
    "ديسمبر": 12, "كانون الأول": 12,
}


def normalize_arabic(text: str) -> str:
    text = araby.strip_tashkeel(text)
    text = araby.strip_tatweel(text)
    text = araby.normalize_alef(text)
    text = araby.normalize_teh(text)
    return re.sub(r"\s+", " ", text).strip()


def _contains_word(normalized: str, word: str) -> bool:
    """Word-boundary containment, not plain substring: "لا" (no) is also the
    last two characters of ordinary, unrelated words such as "طويلاً" (long)
    or "أولاً" (firstly), which a bare `word in normalized` check would flag
    as a "no" answer. \\w is Unicode-aware in Python's re by
    default, so the lookarounds sit at the boundary between Arabic letters
    and whitespace or punctuation.
    """
    return re.search(
        rf"(?<!\w){re.escape(normalize_arabic(word).lower())}(?!\w)", normalized.lower()
    ) is not None


def parse_arabic_boolean(text: str) -> bool | None:
    """Returns True, False, or None for an answer that commits to neither.

    The order matters. Refusals come first, because every common Arabic
    refusal opens with the no-word ("لا أعرف", I do not know) and would
    otherwise be scored as a confident "no". No-words come before
    yes-words, because negative phrasings embed a yes-word: "غير صحيح" (not
    correct) contains "صحيح" (correct), so a no-word hit has to win.

    This is a word list rather than NLU, so it is wrong on any negation it
    does not list.
    """
    normalized = normalize_arabic(text)
    if any(_contains_word(normalized, phrase) for phrase in _REFUSALS):
        return None
    for word in _NO_WORDS:
        if _contains_word(normalized, word):
            return False
    for word in _YES_WORDS:
        if _contains_word(normalized, word):
            return True
    return None


def extract_numbers(text: str) -> set[float]:
    """Every number the text states, whether in ASCII digits, Arabic-Indic
    digits, or spelled out up to ten. Thousands separators are stripped so
    "1,500" reads as one number rather than two.
    """
    folded = normalize_arabic(text).translate(_ARABIC_INDIC)
    folded = re.sub(r"(?<=\d)[,،](?=\d{3}\b)", "", folded)
    # The minus sign only counts as a sign when nothing numeric precedes it.
    # Without that guard an ISO gold date, "1969-07-20", parsed as
    # {1969, -7, -20} and could never match a date written any other way.
    found = {float(m) for m in re.findall(r"(?<![\d.])-?\d+(?:\.\d+)?", folded)}
    for word, value in _SPELLED_NUMBERS.items():
        if _contains_word(folded, word):
            found.add(float(value))
    return found


def _leading_number(text: str) -> float | None:
    """The first number the answer states, in reading order, whether it is
    written in digits or spelled out. That is the number the answer is
    offering; anything after it is supporting detail.

    Reading order matters: "ثلاثة أفلام: ... (2007)"
    leads with the spelled-out three, not with the year, so a digit-first
    search returns the wrong answer. Both forms are located and the earlier
    position wins.
    """
    folded = normalize_arabic(text).translate(_ARABIC_INDIC)
    folded = re.sub(r"(?<=\d)[,،](?=\d{3}\b)", "", folded)
    best: tuple[int, float] | None = None
    m = re.search(r"(?<![\d.])-?\d+(?:\.\d+)?", folded)
    if m:
        best = (m.start(), float(m.group()))
    for word, value in _SPELLED_NUMBERS.items():
        # _contains_word normalises the word itself, so the position has to
        # be looked up with the normalised form to agree with it.
        pos = folded.lower().find(normalize_arabic(word).lower())
        if pos >= 0 and _contains_word(folded, word) and (best is None or pos < best[0]):
            best = (pos, float(value))
    return best[1] if best else None


_IMPERIAL = re.compile(r"""(\d+)\s*(?:'|′)\s*(\d+(?:\.\d+)?)?\s*(?:"|″)?""")


def _imperial_to_inches(text: str) -> float | None:
    """5'7" as a single value in inches. Mintaka states 18 of the 655
    numerical golds this way, all of them heights.
    """
    m = _IMPERIAL.search(text)
    if not m:
        return None
    feet = float(m.group(1))
    inches = float(m.group(2)) if m.group(2) else 0.0
    return feet * 12 + inches


def answer_correct_numerical(generated_text: str, gold_text: str) -> bool:
    """The number the answer *leads with* has to be the gold value.

    A rule of "the gold is among the numbers the answer states anywhere"
    credits an answer for any number it happens to mention, and the arms do
    not mention numbers at equal rates. The no-context arm hedges and
    explains: for aya-expanse:8b, 15.9% of its numerical answers state more
    than one number, against 5.3% for graph-walk and 3.7% for retrieval
    (scripts/07_review_numbers.py, section 4). Such a rule would
    give the control more chances to be right by accident.

    "الجواب: 1" and "تم ترشيحه لجائزة أوسكار واحدة" still score correct
    against gold "1", because the gold is the first number each states.
    "4 ميداليات فضية و ميدالية برونزية واحدة" does not.

    Two gold shapes get their own rule:

    Imperial heights, 18 golds written like 5'7". Matching any of {5, 7}
    would credit "1.80 متر (6 أقدام و 7 بوصات)" against gold 5'7" because of
    the 7. Both sides are converted to inches and compared with a 1-inch
    tolerance, and a metric answer is converted too.

    Multi-value golds, 6 of them, e.g. "1950 1998" for a question asking
    which years Brazil reached a World Cup final without winning. These
    need every gold value present, the containment rule the date matcher
    already uses, not any single one of them.
    """
    gold_numbers = extract_numbers(gold_text)
    if not gold_numbers:
        return _fuzzy_text_match(generated_text, gold_text, DEFAULT_FUZZY_THRESHOLD)

    gold_inches = _imperial_to_inches(gold_text)
    if gold_inches is not None:
        return _height_matches(generated_text, gold_inches)

    if len(gold_numbers) > 1:
        return gold_numbers <= extract_numbers(generated_text)

    return _leading_number(generated_text) in gold_numbers


_ARABIC_FEET = re.compile(
    r"(\d+(?:\.\d+)?)\s*اقدام?(?:\s*و\s*(\d+(?:\.\d+)?)\s*بوصات?)?"
)
_CM = re.compile(r"(\d+(?:\.\d+)?)\s*(?:سم|cm)")
_METRES = re.compile(r"(\d+(?:\.\d+)?)\s*(?:متر|m\b)")


def _height_matches(generated_text: str, gold_inches: float) -> bool:
    """A height answer is correct within one inch, however it is written.

    Arabic answers state heights four ways: 5'7", the same in Arabic words
    ("5 أقدام و 7 بوصات"), centimetres, or metres, and often two of
    them in one sentence. Any one being right is enough, since they are
    restatements of a single claim rather than separate guesses.
    """
    folded = normalize_arabic(generated_text).translate(_ARABIC_INDIC)
    candidates = []
    stated = _imperial_to_inches(folded)
    if stated is not None:
        candidates.append(stated)
    m = _ARABIC_FEET.search(folded)
    if m:
        inches = float(m.group(2)) if m.group(2) else 0.0
        candidates.append(float(m.group(1)) * 12 + inches)
    for m in _CM.finditer(folded):
        candidates.append(float(m.group(1)) / 2.54)
    for m in _METRES.finditer(folded):
        candidates.append(float(m.group(1)) * 100 / 2.54)
    return any(abs(c - gold_inches) <= 1.0 for c in candidates)


def _date_components(text: str) -> set[float]:
    components = extract_numbers(text)
    normalized = normalize_arabic(text)
    for name, number in _ARABIC_MONTHS.items():
        if normalize_arabic(name) in normalized:
            components.add(float(number))
    return components


def answer_correct_date(generated_text: str, gold_text: str) -> bool:
    """Every component of the gold date has to appear. A year alone against
    a full gold date is incorrect on purpose: "1969" is not an answer to a
    question whose gold answer is 1969-07-20. Arabic month names count as
    their number, so "20 يوليو 1969" matches gold "1969-07-20".
    """
    gold = _date_components(gold_text)
    if not gold:
        return _fuzzy_text_match(generated_text, gold_text, DEFAULT_FUZZY_THRESHOLD)
    return gold <= _date_components(generated_text)


def _fuzzy_text_match(generated: str, gold: str, fuzzy_threshold: float) -> bool:
    a, b = normalize_arabic(generated), normalize_arabic(gold)
    if not a or not b:
        return False
    return a == b or fuzz.ratio(a, b) >= fuzzy_threshold


def answer_correct_entity(
    generated_text: str,
    gold_labels_ar: tuple[str, ...],
    fuzzy_threshold: float = DEFAULT_FUZZY_THRESHOLD,
    gold_labels_en: tuple[str, ...] = (),
) -> bool:
    """True if generated_text matches any one of the gold entities: a
    list-type question can have more than one correct entity, and matching
    any one of them counts as correct.

    English is used for one entity only when that entity has no Arabic label
    at all, not as a second chance for every answer. 7.6% of Mintaka's test
    split has at least one gold entity Wikidata carries no Arabic name for
    ("Take Me as I Am", "Sharron Angle"), and scoring those against an empty
    string marks every model wrong whatever it answered. Keeping the
    fallback per entity rather than per question stops it loosening the
    metric elsewhere.
    """
    effective = [
        ar or (gold_labels_en[i] if i < len(gold_labels_en) else "")
        for i, ar in enumerate(gold_labels_ar)
    ]
    return any(_fuzzy_text_match(generated_text, label, fuzzy_threshold) for label in effective if label)


def answer_correct_boolean(generated_text: str, gold_bool: bool) -> bool:
    parsed = parse_arabic_boolean(generated_text)
    return parsed is not None and parsed == gold_bool


def answer_correct_text(generated_text: str, gold_text: str, fuzzy_threshold: float = DEFAULT_FUZZY_THRESHOLD) -> bool:
    return _fuzzy_text_match(generated_text, gold_text, fuzzy_threshold)


def score_answer(
    generated_text: str,
    answer_type: str,
    answer_labels_ar: tuple[str, ...],
    answer_text: str | None,
    fuzzy_threshold: float = DEFAULT_FUZZY_THRESHOLD,
    answer_labels_en: tuple[str, ...] = (),
) -> bool:
    if answer_type == "entity":
        # An entity row whose gold has no QID and no label carries its answer
        # as a free-text mention instead (see mintaka_loader.parse_question).
        # Route those to text matching rather than to the label matcher, which
        # would match against an empty list and return False for every model
        # and every arm alike.
        if not any(answer_labels_ar) and not any(answer_labels_en):
            return answer_correct_text(generated_text, answer_text, fuzzy_threshold) if answer_text else False
        return answer_correct_entity(generated_text, answer_labels_ar, fuzzy_threshold, answer_labels_en)
    if answer_type == "boolean":
        gold_bool = str(answer_text).strip().lower() == "true"
        return answer_correct_boolean(generated_text, gold_bool)
    if answer_text is None:
        return False
    if answer_type == "numerical":
        return answer_correct_numerical(generated_text, answer_text)
    if answer_type == "date":
        return answer_correct_date(generated_text, answer_text)
    return answer_correct_text(generated_text, answer_text, fuzzy_threshold)


@dataclass(frozen=True)
class ScoredItem:
    item_id: str
    correct: bool
    complexity_type: str
    category: str


def aggregate_accuracy(items: list[ScoredItem]) -> dict:
    """Overall accuracy plus the breakdown by complexity_type and category.
    Empty groups are omitted rather
    than reported as 0/0, since a 0% accuracy on zero items is not a
    finding.
    """
    by_type: dict[str, list[bool]] = defaultdict(list)
    by_category: dict[str, list[bool]] = defaultdict(list)
    for item in items:
        by_type[item.complexity_type].append(item.correct)
        by_category[item.category].append(item.correct)

    def rate(flags: list[bool]) -> float:
        return sum(flags) / len(flags) if flags else 0.0

    return {
        "overall_accuracy": rate([i.correct for i in items]),
        "n_items": len(items),
        "by_complexity_type": {k: {"accuracy": rate(v), "n": len(v)} for k, v in sorted(by_type.items())},
        "by_category": {k: {"accuracy": rate(v), "n": len(v)} for k, v in sorted(by_category.items())},
    }
