"""Pulls a bounded-hop Wikidata neighborhood around a known QID set.

The seeds are the QIDs src/qa/mintaka_loader.py::collect_qids finds in the
question set being run. There is no property allowlist: every outgoing
entity-valued property (any wdt: direct claim whose object is a Wikidata
item) is pulled, since Mintaka's questions span many domains (movies, video
games, sport and more) and a fixed property list would miss what some of
them need. Literal values (dates, quantities) are pulled separately by
build_literal_query, for the retrieval corpus only.
"""

import json as json_module
import logging
import time

from SPARQLWrapper import JSON, SPARQLWrapper

logger = logging.getLogger(__name__)


def qid_from_uri(uri: str) -> str:
    return uri.rsplit("/", 1)[-1]


def pid_from_uri(uri: str) -> str:
    return uri.rsplit("/", 1)[-1]


def _client(endpoint: str, user_agent: str, timeout_s: int = 90) -> SPARQLWrapper:
    sparql = SPARQLWrapper(endpoint)
    sparql.agent = user_agent
    sparql.setReturnFormat(JSON)
    sparql.setTimeout(timeout_s)
    return sparql


# Errors that mean "the network went away", as opposed to "this query is
# wrong". A local connection drop resolves itself and deserves a longer wait;
# a malformed query never will and should fail fast rather than burn ten
# minutes of backoff proving it.
_TRANSIENT_MARKERS = (
    "getaddrinfo",        # DNS resolution failed, i.e. the connection dropped
    "timed out", "timeout",
    "connection", "econnreset", "broken pipe",
    "temporarily unavailable", "503", "502", "504",
    # A truncated JSON body: the endpoint began answering and stopped partway,
    # so json.loads reports an unterminated string or an unexpected end. It
    # reads like a parse error, but the query was fine and the same request
    # succeeds on a retry, so it belongs on the long budget.
    "unterminated string", "expecting value", "unexpected end", "expecting property name",
)


def _is_transient(exc: Exception) -> bool:
    """True for failures that a retry can plausibly fix.

    Includes JSONDecodeError by type as well as by message, since a truncated
    response is a transport failure wearing a parser's error text.
    """
    if isinstance(exc, json_module.JSONDecodeError):
        return True
    return any(m in str(exc).lower() for m in _TRANSIENT_MARKERS)


def _run(
    sparql: SPARQLWrapper,
    query: str,
    max_retries: int = 5,
    backoff_s: float = 10.0,
    transient_max_retries: int = 8,
    max_wait_s: float = 60.0,
) -> list[dict]:
    """Runs one SPARQL query, retrying on failure.

    Two budgets, because two different things go wrong. A wrong query fails
    identically every time and gets `max_retries` attempts. A dropped
    connection gets `transient_max_retries`, with the wait capped at
    `max_wait_s` rather than growing without limit.

    The batch-level caller catches a final failure and carries on, so a
    skipped batch leaves a hole in the graph rather than a crash. Such a hole
    is easy to miss, because a starved graph-walk arm looks like a weak
    result. The transient budget therefore tolerates roughly 5.5 minutes of
    downtime (10+20+30+40+50+60+60+60 s).
    """
    sparql.setQuery(query)
    last_error = None
    attempt = 0
    while True:
        attempt += 1
        try:
            raw = sparql.query().response.read().decode("utf-8")
            result = json_module.loads(raw, strict=False)
            return result["results"]["bindings"]
        except Exception as exc:  # SPARQLWrapper raises plain Exception/URLError on HTTP errors
            last_error = exc
            budget = transient_max_retries if _is_transient(exc) else max_retries
            if attempt >= budget:
                break
            is_rate_limited = "429" in str(exc)
            wait_s = max_wait_s if is_rate_limited else min(max_wait_s, backoff_s * attempt)
            logger.warning(
                "SPARQL query failed (attempt %d/%d): %s. Waiting %.0fs before retry.",
                attempt, budget, exc, wait_s,
            )
            time.sleep(wait_s)
    raise RuntimeError(f"SPARQL query failed after {attempt} attempts") from last_error


def build_neighborhood_query(qids: list[str], labels_language: str = "ar", row_limit: int = 10000) -> str:
    """One VALUES-bounded batch of QIDs. FILTER(ISIRI(?tail)) keeps only
    entity-valued edges, dropping literal-valued claims (dates, numbers,
    strings), which are not walkable.

    row_limit caps the response size the server has to compute and send
    before cap_triples_per_head runs client-side. With no property allowlist
    and no per-head bound, one hub entity in a large batch can produce a
    response that is cut off mid-stream at the same byte offset on every
    retry. A bare LIMIT does not split rows evenly across heads (SPARQL
    result order within a VALUES batch is implementation-defined); it bounds
    the worst case and is not meant to be fair.
    """
    qid_values = " ".join(f"wd:{q}" for q in qids)
    return f"""
    SELECT ?head ?prop ?tail ?tailLabel WHERE {{
      VALUES ?head {{ {qid_values} }}
      ?head ?directProp ?tail.
      ?prop wikibase:directClaim ?directProp.
      FILTER(ISIRI(?tail))
      ?tail rdfs:label ?tailLabel FILTER(LANG(?tailLabel) = "{labels_language}").
    }}
    LIMIT {row_limit}
    """


def parse_neighborhood_rows(rows: list[dict]) -> list[tuple[str, str, str, str]]:
    """Returns (head_qid, property_pid, tail_qid, tail_label) tuples."""
    triples = []
    for row in rows:
        head = qid_from_uri(row["head"]["value"])
        prop = pid_from_uri(row["prop"]["value"])
        tail = qid_from_uri(row["tail"]["value"])
        label = row["tailLabel"]["value"]
        triples.append((head, prop, tail, label))
    return triples


def cap_triples_per_head(triples: list[tuple[str, str, str, str]], max_per_head: int) -> list[tuple[str, str, str, str]]:
    """Keeps at most max_per_head triples per distinct head QID, first-seen
    order. A hub entity (e.g. a country, or an "instance of human" class)
    can have thousands of outgoing edges; without a cap, iterative
    multi-hop expansion (scripts/01_collect_qids_and_pull_graph.py) could
    make the pulled graph and the SPARQL query volume explode after only
    one or two hops.
    """
    counts: dict[str, int] = {}
    kept = []
    for triple in triples:
        head = triple[0]
        counts[head] = counts.get(head, 0) + 1
        if counts[head] <= max_per_head:
            kept.append(triple)
    return kept


def expand_neighborhood(
    fetch_fn,
    seed_qids: set[str],
    already_cached: set[str],
    cached_triples_by_head: dict[str, list[tuple[str, str, str, str]]],
    max_hops: int,
    max_neighbors_per_qid: int,
    stop_after_hop: int | None = None,
) -> tuple[list[tuple[str, str, str, str]], set[str]]:
    """Iterative multi-hop expansion: hop 1 pulls the seeds' neighbors, hop
    2 pulls those neighbors' neighbors, and so on, up to max_hops. Used by
    scripts/01_collect_qids_and_pull_graph.py; kept here so it can be unit
    tested with a fake fetch_fn instead of a live SPARQLWrapper.

    already_cached and cached_triples_by_head describe what a previous run
    already pulled and wrote to the cache (configs/graph_walk.yaml's
    graph_cache_dir). A head in already_cached is not re-queried, so a
    larger scale tier only pulls what is new. Its cached tails are still
    added to this run's BFS frontier. Without that, a QID cached as a hop-2
    neighbor in a smaller run that becomes a seed in a larger run would be
    skipped as "already cached" and its neighbors would never be expanded.

    stop_after_hop halts the expansion after that hop and logs the frontier
    the next hop would have queried, split into the cached part and the part
    needing fresh SPARQL. It lets the branching factor be measured before
    committing to a full pull. Whatever this hop pulled is still returned
    and cached, so a stopped run is a smaller completed pull.

    fetch_fn(qids) -> (triples, failed_qids), matching
    fetch_neighborhood(sparql, qids)'s own return shape: failed_qids is
    whichever of qids came back unresolved (a batch that failed every
    retry), not merely absent from triples.

    Returns (newly_fetched_triples, newly_queried_heads): newly_queried_heads
    lists heads this call sent to fetch_fn and got a real answer for,
    including a genuine zero-edge result, so the caller can write a "no
    outgoing edges" sentinel row for them. A head whose batch failed every
    retry is left out of newly_queried_heads. It gets no sentinel row and
    stays eligible for a retry on a later run, instead of being cached as a
    false "has no outgoing edges" that would never be re-queried.
    """
    frontier = set(seed_qids)
    visited: set[str] = set()
    queried_this_run: set[str] = set()
    all_new_triples: list[tuple[str, str, str, str]] = []

    for hop in range(1, max_hops + 1):
        hop_nodes = frontier - visited
        if not hop_nodes:
            logger.info("hop %d: nothing new to expand, stopping expansion early", hop)
            break

        to_query = sorted(n for n in hop_nodes if n not in already_cached)
        reused_heads = hop_nodes - set(to_query)
        logger.info(
            "hop %d: querying %d new QIDs, reusing %d already-cached QIDs",
            hop, len(to_query), len(reused_heads),
        )

        fetched, failed = fetch_fn(to_query) if to_query else ([], set())
        if failed:
            logger.warning("hop %d: %d QIDs failed and will not be cached as queried: %s", hop, len(failed), sorted(failed))
        capped = cap_triples_per_head(fetched, max_neighbors_per_qid)
        all_new_triples.extend(capped)
        queried_this_run.update(set(to_query) - failed)

        reused_triples = [t for head in reused_heads for t in cached_triples_by_head.get(head, [])]

        visited.update(hop_nodes)
        next_tails = {t[2] for t in capped} | {t[2] for t in reused_triples}
        frontier = next_tails - visited

        if stop_after_hop is not None and hop >= stop_after_hop:
            pending_new = frontier - already_cached
            logger.info(
                "stopping after hop %d as requested. Next hop's frontier: %d QIDs "
                "(%d already cached, %d needing a fresh query). Branching factor "
                "this hop: %.1f new QIDs per queried QID.",
                hop, len(frontier), len(frontier & already_cached), len(pending_new),
                len(frontier) / len(hop_nodes) if hop_nodes else 0.0,
            )
            break

    return all_new_triples, queried_this_run


def build_literal_query(qids: list[str], row_limit: int = 10000) -> str:
    """Literal-valued claims (dates and quantities) for a batch of heads.

    The companion to build_neighborhood_query, which filters to
    ISIRI(?tail) and so drops every date and number. That is right for the
    graph-walk arm, since a date is a value rather than an edge to traverse,
    and wrong for the retrieval corpus. On the stratified scale-100 tier,
    comparative questions score 0% gold-in-context under every path ranking
    tried, because "who is older, X or Y" needs P569 (date of birth) for
    both, and P569 is a literal. 45 of that tier's 100 questions have a
    numerical, boolean or date gold answer.

    Restricted to Quantity and Time, following Mintaka's own definitions of
    the question types that need them (Sen, Aji and Saffari, 2022, COLING,
    sections 3 and 4.1):

    - Comparative questions are defined there as "questions that compare two
      objects on a given attribute (e.g., age, height)". Age is P569, a Time
      value; height is P2048, a Quantity. Those two datatypes are precisely
      what the definition names.
    - For Superlative and Count, the annotators were asked for "a numerical
      value as part of the answer": a Superlative answer carries both the
      entity and the quantity that makes it the maximum, their example being
      Missouri River together with 2,341 miles. So a Superlative question
      turns on a Quantity attribute even though its gold answer is an entity.
    - Table 2's answer-type split is entity 0.72, boolean 0.14, numerical
      0.07, date 0.06, string 0.001. Numerical and date are Quantity and Time.
      String is 0.1% of the dataset and is not worth the corpus noise.

    ExternalId is excluded: an external identifier is a key into another
    database (an IMDb or VIAF id) and carries no fact a question could ask
    about. Filtering on wikibase:propertyType rather than on the value's RDF
    datatype is what makes this possible, since an ExternalId and a real
    String are both plain strings once serialised.

    Values come from the truthy wdt: claim, so a Quantity arrives without
    its unit (the unit lives on the full statement node). A height of 1.88
    metres reads as "1.88". This is a known limitation: the unit-bearing
    form needs the statement-level p:/psv: path, a much heavier query.
    """
    qid_values = " ".join(f"wd:{q}" for q in qids)
    return f"""
    SELECT ?head ?prop ?value WHERE {{
      VALUES ?head {{ {qid_values} }}
      ?head ?directProp ?value.
      ?prop wikibase:directClaim ?directProp.
      ?prop wikibase:propertyType ?ptype.
      FILTER(!ISIRI(?value))
      FILTER(?ptype IN (wikibase:Quantity, wikibase:Time))
    }}
    LIMIT {row_limit}
    """


def _format_literal(raw: str, datatype: str | None) -> str:
    """Renders a raw SPARQL literal as something worth embedding.

    Wikidata dates arrive as full xsd:dateTime ("1969-07-20T00:00:00Z").
    The time part is always midnight for a date-precision claim, so it is
    noise in every fact sentence it appears in, and it would push an
    embedding model toward matching on the zeros. Trimmed to the date.
    Quantities arrive with a leading "+" on positives, which is dropped.
    """
    if datatype and datatype.endswith("dateTime"):
        return raw.split("T", 1)[0].lstrip("+")
    return raw.lstrip("+") if raw.startswith("+") else raw


def parse_literal_rows(rows: list[dict]) -> list[tuple[str, str, str]]:
    """Returns (head_qid, property_pid, formatted_value) triples. Three
    fields rather than the four parse_neighborhood_rows returns: there is
    no tail QID, which is exactly what makes these facts non-walkable.
    """
    out = []
    for row in rows:
        head = qid_from_uri(row["head"]["value"])
        prop = pid_from_uri(row["prop"]["value"])
        value = _format_literal(row["value"]["value"], row["value"].get("datatype"))
        out.append((head, prop, value))
    return out


def fetch_literals(
    sparql: SPARQLWrapper,
    qids: list[str],
    chunk_size: int = 25,
    sleep_between_chunks_s: float = 2.0,
) -> tuple[list[tuple[str, str, str]], set[str]]:
    """Same batching, per-batch failure handling and return shape as
    fetch_neighborhood; see that function for why a failed batch is
    reported rather than silently folded into "no result".
    """
    all_literals: list[tuple[str, str, str]] = []
    failed_qids: set[str] = set()
    for i in range(0, len(qids), chunk_size):
        batch = qids[i : i + chunk_size]
        try:
            rows = _run(sparql, build_literal_query(batch))
        except RuntimeError as exc:
            logger.error(
                "literal batch %d-%d of %d QIDs failed after repeated retries (%s); skipping",
                i, i + len(batch), len(qids), exc,
            )
            failed_qids.update(batch)
            time.sleep(sleep_between_chunks_s)
            continue
        all_literals.extend(parse_literal_rows(rows))
        logger.info(
            "literals: batch %d-%d of %d QIDs -> %d facts so far",
            i, i + len(batch), len(qids), len(all_literals),
        )
        time.sleep(sleep_between_chunks_s)
    return all_literals, failed_qids


def drop_excluded_properties(
    triples: list[tuple[str, str, str, str]],
    excluded: set[str] | list[str] | None,
) -> list[tuple[str, str, str, str]]:
    """Removes edges on configs/graph_walk.yaml's excluded_properties.

    Must run before scope_to_seeds, not after: dropping the edge that leads
    to a Wikimedia category page is what makes that page unreachable, so its
    own outgoing edges fall out of the tier with it. Filtering afterwards
    would leave the category's subtree in the corpus while removing only the
    single edge pointing at it.

    Both arms read the filtered graph. The retrieval corpus sheds noise,
    and the walk can no longer hop into a category page and back out into
    an unrelated topic.
    """
    if not excluded:
        return triples
    blocked = set(excluded)
    return [t for t in triples if t[1] not in blocked]


def scope_to_seeds(
    triples: list[tuple[str, str, str, str]],
    seed_qids: set[str],
    max_hops: int,
) -> list[tuple[str, str, str, str]]:
    """The subset of the cache that belongs to the tier being run: the
    triples expand_neighborhood would have pulled for these seeds at this
    hop count, and no others.

    The cache is cumulative, since a larger scale tier only pulls what it
    does not already have. That makes it a union of every tier and sample
    run on this machine, which is fine as a cache and wrong as a corpus.
    Without this filter, scripts/02 would embed the whole file: at scale 100
    that is 437,861 triples where the tier's own graph is 69,704. The corpus
    would also depend on run history, so a fresh clone would get a different
    retrieval corpus from a machine that ran another sample first.

    Directed, matching the pull rather than the walk: the pull queries
    heads at BFS depth 0 to max_hops-1 and stores their outgoing edges, so
    the tier's graph is exactly the edges reachable that way.
    src/qa/graph_walk.py::build_adjacency then makes its own traversal
    undirected on top of this, which is a property of the walk, not of
    which facts the tier contains.
    """
    by_head: dict[str, list[tuple[str, str, str, str]]] = {}
    for triple in triples:
        by_head.setdefault(triple[0], []).append(triple)

    kept: list[tuple[str, str, str, str]] = []
    visited: set[str] = set()
    frontier = set(seed_qids)
    for _hop in range(max_hops):
        hop_nodes = frontier - visited
        if not hop_nodes:
            break
        visited |= hop_nodes
        next_frontier: set[str] = set()
        # sorted(): iterating the set directly would make the order of `kept`,
        # and so the walk's adjacency lists, BFS discovery order and ranking
        # ties, depend on Python's per-process string hash seed. Two runs of
        # scripts/03 then share only ~95% of context lines.
        for node in sorted(hop_nodes):
            for triple in by_head.get(node, ()):
                kept.append(triple)
                next_frontier.add(triple[2])
        frontier = next_frontier - visited
    return kept


def build_property_label_query(pids: list[str], labels_language: str = "ar") -> str:
    """Property labels ("director", not "P57") for the sentence-building
    step in src/qa/retrieval.py::build_retrievable_facts. A fact rendered
    with a raw PID instead of a label would be unreadable to both the
    embedding model and the answer LLM.
    """
    pid_values = " ".join(f"wd:{p}" for p in pids)
    return f"""
    SELECT ?prop ?propLabel WHERE {{
      VALUES ?prop {{ {pid_values} }}
      ?prop rdfs:label ?propLabel FILTER(LANG(?propLabel) = "{labels_language}").
    }}
    """


def parse_property_label_rows(rows: list[dict]) -> dict[str, str]:
    """Returns {pid: label}."""
    out: dict[str, str] = {}
    for row in rows:
        pid = pid_from_uri(row["prop"]["value"])
        out[pid] = row["propLabel"]["value"]
    return out


def fetch_property_labels(
    sparql: SPARQLWrapper,
    pids: list[str],
    chunk_size: int = 200,
    labels_language: str = "ar",
) -> dict[str, str]:
    """labels_language is threaded through so a caller can make a second pass
    in English for the properties Wikidata has no Arabic label for; see
    scripts/02_run_retrieval.py::ensure_property_labels.
    """
    out: dict[str, str] = {}
    for i in range(0, len(pids), chunk_size):
        batch = pids[i : i + chunk_size]
        rows = _run(sparql, build_property_label_query(batch, labels_language=labels_language))
        out.update(parse_property_label_rows(rows))
    return out


def fetch_neighborhood(
    sparql: SPARQLWrapper,
    qids: list[str],
    chunk_size: int = 25,
    sleep_between_chunks_s: float = 2.0,
) -> tuple[list[tuple[str, str, str, str]], set[str]]:
    """Pulls neighborhoods in batches of chunk_size QIDs.

    chunk_size=25 because this query has no class or country filter
    narrowing ?head. At 100, one batch's combined response was too large to
    complete even with row_limit, and failed every retry at the same byte
    offset. Smaller batches bound how many heads can combine into one
    oversized response.

    A batch can still fail every retry if one QID in it is too expensive for
    the endpoint's server-side timeout. Per-batch failures are caught and
    skipped, so one bad batch does not crash the multi-hop expansion and
    lose every batch already fetched.

    Returns (triples, failed_qids). A skipped batch's QIDs go into
    failed_qids rather than counting as "no result": the caller
    (expand_neighborhood) must not cache a failed QID as a confirmed empty
    head, or it would never be retried.
    """
    all_triples: list[tuple[str, str, str, str]] = []
    failed_qids: set[str] = set()
    for i in range(0, len(qids), chunk_size):
        batch = qids[i : i + chunk_size]
        try:
            rows = _run(sparql, build_neighborhood_query(batch))
        except RuntimeError as exc:
            logger.error(
                "batch %d-%d of %d QIDs failed after repeated retries (%s); skipping this batch (%s), "
                "keeping %d triples already collected",
                i, i + len(batch), len(qids), exc, batch, len(all_triples),
            )
            failed_qids.update(batch)
            time.sleep(sleep_between_chunks_s)
            continue
        triples = parse_neighborhood_rows(rows)
        all_triples.extend(triples)
        logger.info(
            "neighborhood: batch %d-%d of %d QIDs -> %d triples so far",
            i, i + len(batch), len(qids), len(all_triples),
        )
        time.sleep(sleep_between_chunks_s)
    return all_triples, failed_qids
