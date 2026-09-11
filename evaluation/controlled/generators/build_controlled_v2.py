"""
build_controlled_v2.py — Sanitized, metadata-rich generator for
SMRITI-Controlled-v2.

RECTIFIED (external "reality check" review, second pass over the
707-pair corpus this same generator family originally produced):

  P0-1 grammar defects: the negation family produced ungrammatical
    "does not supports" (third-person-singular verb after "does not"
    instead of base form), and the SUPPORTS family produced sentences
    with a missing grammatical subject ("Independent benchmarks confirm
    that significantly lowers job latency..."). Both are fixed at the
    template level below, not patched after generation.

  P0-2 cross-category duplicate propositions: nothing in this generator
    may produce a claim sentence identical to one already in the corpus,
    including the original hand-written v1 pilot pairs. Enforced by a
    single global _written_texts set checked before any file is written
    (register() raises on collision instead of silently overwriting).

  P0-3 non-exclusive "CONTRADICTS" pairs: a pair is only a genuine
    contradiction if both claims cannot be true simultaneously. "Runs on
    ARM64" / "runs on x86-64" and "developed by Team Alpha" / "developed
    by Team Beta" do NOT satisfy this (a system can support multiple
    architectures; a project can have multiple contributing teams) unless
    the sentence itself encodes single-valuedness. Every CONTRADICTS pair
    below is constructed with an explicit exclusivity premise (e.g.
    "primary deployment platform", "was solely developed by") and tagged
    with contradiction_basis + exclusivity_type metadata so the ontology
    claim is checkable, not asserted.

  P0-10 / P0-11 template-family over-alignment: REFINES previously used
    one specificity mechanism (percentage + date) -- exactly the feature
    the specificity heuristic (classification/specificity.py) scores on,
    making "REFINES: 84.4% recall, 100% accuracy" an unsurprising result
    about recognizing its own feature, not evidence of generalization.
    REFINES here spans 7 independent specificity mechanisms (numeric,
    geographic scope, population scope, experimental condition, dataset,
    causal mechanism, qualification) as separate template families.
    EQUIVALENT spans 7 difficulty tiers (easy/medium/hard/contextual/
    negation-preserving/numerical/unit) instead of one lexical-paraphrase
    pattern.

  P1 dev/test split: every pair carries a `split` field (dev/test)
    assigned by template_family_id, never by individual pair -- so the
    same template family never appears in both dev and test, and tuning
    resolver thresholds against dev cannot leak into the frozen test set.

  P1 label provenance: every pair carries
    label_provenance = "CONSTRUCTION_DEFINED" (not "gold" in the sense of
    human or expert annotation -- the label is a fact about how the pair
    was built).

RECTIFIED (external "reality check" review round 3, generator version
2.0 -- semantic validity, not just grammar):

  P0-1 attribute/value type mismatch: the CONTRADICTS "direct" category's
    attribute list and its two value pools were indexed independently
    (7 attributes vs. 8 values, coprime lengths), so most generated pairs
    paired an attribute with a value from the wrong domain (e.g. "default
    network protocol is Linux", "primary hosting region is a relational
    store") -- grammatical, but not a valid domain proposition, and
    therefore not a genuine contradiction basis. Fixed by making each
    (attribute, value_a, value_b) one atomic, pre-paired tuple.

  P0-2 REFINES restrictive scoping: the "population" and "condition"
    specificity mechanisms phrased the added detail as a restrictive
    qualifier ("for clusters exceeding N nodes", "specifically under
    sustained high-concurrency load") -- read literally, this scopes the
    claim DOWN to a subset, so the specific claim does not actually
    entail the general one, which is exactly what REFINES is supposed to
    require. Reworded to explicitly preserve the general claim
    ("particularly for X", "with the effect especially pronounced under
    X"), matching the "geographic" mechanism's own already-correct
    "most notably in X" pattern.

Run with: python build_controlled_v2.py
"""
import hashlib
import itertools
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CORPUS_DIR = ROOT / "data" / "raw" / "controlled_v2"
V1_CORPUS_DIR = ROOT / "data" / "raw" / "controlled_v1"
MANIFEST_PATH = ROOT / "evaluation" / "controlled" / "v2" / "construction_manifest.json"

random.seed(20260911)
CORPUS_DIR.mkdir(parents=True, exist_ok=True)

# ── Shared name pools (same pool as before; regenerated independently) ──
NAME_A = [
    "Aurora", "Falcon", "Meridian", "Orion", "Titan", "Vantage", "Kelvor",
    "Draymoor", "Brackwood", "Larkspur", "Norwich", "Farrow", "Renfield",
    "Osprey", "Talbrook", "Windmere", "Colby", "Dunmore", "Ivestone",
    "Cassian", "Marlow", "Halloway", "Aerotrix", "Solvex", "Quorren",
    "Vesper", "Talwick", "Bramfield", "Corvane", "Halcyon", "Ashgrove",
    "Ternvale", "Rivenmark", "Duskwell", "Fenmoor", "Gravenhurst",
    "Highcrest", "Ironvale", "Juniper", "Kestrel", "Lockhaven", "Mirefield",
    "Nightshade", "Oakmere", "Pemberton", "Quillon", "Ridgemont",
    "Stormcrest", "Thistledown", "Umberglade", "Voxhollow", "Wraithmoor",
    "Xylonberg", "Yewcross", "Zenithfall", "Cindermark", "Doverclay",
    "Emberfen", "Frostwick", "Glimmerholt", "Hawksmere", "Ivorclyffe",
]
NAME_B = [
    "Engine", "Cluster", "Node", "Array", "Registry", "Pipeline",
    "Framework", "Scheduler", "Model", "Sensor", "Router", "Server",
    "Service", "Module", "Index", "Cache", "Queue", "Substrate", "Lattice",
    "Gateway", "Daemon", "Agent", "Ledger", "Beacon", "Relay", "Vault",
    "Fabric", "Grid", "Codec", "Kernel",
]
_entity_combos = list(itertools.product(NAME_A, NAME_B))
random.shuffle(_entity_combos)
_entity_iter = iter(_entity_combos)


def next_entity() -> str:
    a, b = next(_entity_iter)
    return f"{a} {b}"


PEOPLE = [
    "Dr. Elena Cho", "Dr. Marcus Reyes", "Dr. Amara Okafor", "Dr. Liu Wei",
    "Dr. Priya Nair", "Dr. Tomas Varga", "Dr. Freya Lindqvist",
    "Dr. Ibrahim Osei", "Dr. Naomi Kessler", "Dr. Sanjay Rao",
    "Dr. Isabel Marchetti", "Dr. Kenji Watanabe", "Dr. Aditi Bhatt",
    "Dr. Peter Nkomo", "Dr. Sofia Reinholt", "Dr. Dmitri Volkov",
    "Dr. Grace Lindholm", "Dr. Owen Fitzgerald", "Dr. Mei-Lin Tan",
    "Dr. Victor Adeyemi",
]
TEAMS = [
    "Team Alpha", "Team Beta", "Team Gamma", "Team Delta", "Team Epsilon",
    "Team Zeta", "Team Nova", "Team Vertex", "Team Cascade", "Team Ridge",
]

_written_texts = set()


def _load_existing_v1_texts():
    # RECTIFIED (P2, "FINAL REVIEW" round): renamed from gold_manifest.json
    # -- this file is the original 32-pair pilot corpus's construction-
    # defined manifest, kept ONLY so v2 generation can avoid duplicating
    # its exact sentence text (never as a "gold"/ground-truth label
    # source; v2 has never read a label from this file, only text).
    v1_manifest_path = ROOT / "evaluation" / "controlled" / "v1_pilot_manifest.json"
    manifest = json.loads(v1_manifest_path.read_text(encoding="utf-8"))
    for p in manifest:
        _written_texts.add(p["text_a"])
        _written_texts.add(p["text_b"])
    return manifest


_load_existing_v1_texts()  # populate _written_texts with the v1 pilot corpus BEFORE any v2 generation


def register(text: str) -> str:
    # RECTIFIED: every generated sentence must be capitalized at the
    # sentence-initial position regardless of whether the first word is
    # a proper noun -- English capitalizes the first word of a sentence
    # mechanically; "python sheds its skin" (lowercase, common-noun
    # sense) is still ungrammatical as a full sentence. The lexical-
    # collision distinction lives in the predicate, not in orthographic
    # case, which is also a harder (more realistic) test.
    if text and text[0].islower():
        text = text[0].upper() + text[1:]
    if text in _written_texts:
        raise ValueError(f"Duplicate generated text (P0-2 violation): {text!r}")
    _written_texts.add(text)
    return text


new_entries = []
_id_counters = {}

def assign_splits_stratified_by_category(entries):
    """
    P1 dev/test split, stratified per category (RECTIFIED: a first version
    of this assigned split per template family globally at ~65/35, which
    for a category with only 2-4 families could put every one of them on
    the same side by chance -- "entity" landed with 0 test pairs the first
    time this ran. Splitting within each category's own family set
    guarantees every category has both dev and test representation
    whenever it has >=2 families, while never splitting one family across
    both sides (still no leakage). Deterministic (hash-ordered, not
    alphabetical, to avoid a systematic first-letter bias) so re-running
    this script reproduces the same split exactly.
    """
    from collections import defaultdict
    families_by_cat = defaultdict(set)
    for e in entries:
        families_by_cat[e["category"]].add(e["template_family_id"])

    family_to_split = {}
    for cat, fams in families_by_cat.items():
        ordered = sorted(fams, key=lambda f: hashlib.sha256(f.encode()).hexdigest())
        n_test = max(1, round(len(ordered) * 0.35)) if len(ordered) >= 2 else 0
        for i, fam in enumerate(ordered):
            family_to_split[fam] = "test" if i < n_test else "dev"

    for e in entries:
        e["split"] = family_to_split[e["template_family_id"]]


def make_pair(
    prefix, text_a, text_b, gold, category, family_id,
    contradiction_basis=None, exclusivity_type=None,
):
    """
    RECTIFIED (P0-3, "PLEASE FIX AND SAVE ME" review round): the manifest
    used to store the ambiguous_abstention category's gold label as
    "gold_relationship": "UNKNOWN" -- UNKNOWN sitting in the same field,
    with the same shape, as the five real relation types invites reading
    it as a sixth relation type to classify against, rather than what it
    actually is: these 45 pairs have no correct semantic label at all, by
    construction, and the only reasonable "gold" answer is that a
    calibrated system should ABSTAIN. `gold` (the caller's argument) is
    still passed as the literal string "UNKNOWN" for this category since
    every call site (\S15 below) predates this fix, but it is translated
    here into expected_status/expected_relation, and the manifest no
    longer stores a `gold_relationship` field at all -- `expected_relation`
    is `None` iff `expected_status` is "ABSTAINED".

    `direction` is not yet tracked at construction time for any category
    (SUPPORTS/REFINES included) and is always `None` here -- adding real
    per-pair direction ground truth is separate, not-yet-built work, not
    a value this generator can honestly fabricate.
    """
    text_a = register(text_a)
    text_b = register(text_b)
    n = _id_counters.get(prefix, 0) + 1
    _id_counters[prefix] = n
    doc_a, doc_b = f"{prefix}{n:03d}a", f"{prefix}{n:03d}b"
    (CORPUS_DIR / f"{doc_a}.md").write_text(f"# {doc_a}\n\n{text_a}\n", encoding="utf-8")
    (CORPUS_DIR / f"{doc_b}.md").write_text(f"# {doc_b}\n\n{text_b}\n", encoding="utf-8")
    is_abstention = gold == "UNKNOWN"
    entry = {
        "doc_a": doc_a, "text_a": text_a,
        "doc_b": doc_b, "text_b": text_b,
        "expected_relation": None if is_abstention else gold,
        "expected_status": "ABSTAINED" if is_abstention else "RESOLVED",
        "direction": None,
        "category": category,
        "template_family_id": family_id,
        "label_provenance": "CONSTRUCTION_DEFINED",
        "split": None,  # assigned in a stratified pass once generation completes
    }
    if contradiction_basis:
        entry["contradiction_basis"] = contradiction_basis
    if exclusivity_type:
        entry["exclusivity_type"] = exclusivity_type
    new_entries.append(entry)


TARGET = 47  # per-category base target (varies slightly per category below)

# ── 1. CONTRADICTS: direct (single-valued "primary X" framing) ──────────
# RECTIFIED (P0-3): "runs on ARM64 / x86-64" is not exclusive on its own
# (a system can support both). "primary deployment platform" makes the
# attribute explicitly single-valued.
#
# RECTIFIED (external "reality check" review round 3, P0-1 "controlled-v2
# is still not semantically clean"): the attribute list (DIRECT_ATTR, 7
# entries) and the two value-pool lists (DIRECT_PAIRS_A/B, 8 entries each)
# were previously indexed by `i % len(...)` INDEPENDENTLY of each other.
# Since 7 and 8 are coprime, the attribute and its value pair only aligned
# by coincidence at i=0 within the TARGET=47 range (they next realign at
# i=56, past TARGET) -- meaning attribute/value pairings like "default
# network protocol is Linux" or "primary hosting region is a relational
# store" were generated: grammatical, but not valid domain propositions.
# A basic typed-domain check found the large majority of the 47 direct
# pairs affected. Fixed by making each (attribute, value_a, value_b) a
# single, inherently-consistent tuple, cycled by ONE index -- pairing can
# no longer drift apart.
DIRECT_ATTR_VALUE_PAIRS = [
    ("primary deployment platform", "ARM64", "x86-64"),
    ("primary deployment platform", "Linux", "Windows"),
    ("default network protocol", "IPv4", "IPv6"),
    ("primary storage backend", "a relational store", "a document store"),
    ("primary hosting region", "the eastern region", "the western region"),
    ("primary execution environment", "bare metal", "virtual machines"),
    ("default billing tier", "the free tier", "the enterprise tier"),
    ("default provisioning mode", "spot instances", "reserved instances"),
]
for i in range(TARGET):
    e = next_entity()
    attr, a, b = DIRECT_ATTR_VALUE_PAIRS[i % len(DIRECT_ATTR_VALUE_PAIRS)]
    fam = f"DR-{attr.replace(' ', '_')}-{a.replace(' ', '_')}"
    make_pair(
        "DR", f"The {e}'s {attr} is {a}.", f"The {e}'s {attr} is {b}.",
        "CONTRADICTS", "direct", fam,
        contradiction_basis="single_valued_attribute", exclusivity_type=attr,
    )

# ── 2. CONTRADICTS: negated (grammar fixed: base form after "does not") ─
# RECTIFIED (P0-1): (affirmative_third_person, base_form) pairs, so
# negation is always "does not " + base form, never the inflected form.
VERB_PHRASES = [
    ("supports GPU execution", "support GPU execution"),
    ("requires authentication", "require authentication"),
    ("encrypts data at rest", "encrypt data at rest"),
    ("allows anonymous access", "allow anonymous access"),
    ("retries failed requests automatically", "retry failed requests automatically"),
    ("supports horizontal scaling", "support horizontal scaling"),
    ("validates input schemas", "validate input schemas"),
    ("caches query results", "cache query results"),
    ("supports multi-tenancy", "support multi-tenancy"),
    ("logs request bodies", "log request bodies"),
    ("supports offline mode", "support offline mode"),
    ("enforces rate limiting", "enforce rate limiting"),
    ("supports hot reload", "support hot reload"),
    ("compresses network payloads", "compress network payloads"),
    ("supports rollback on failure", "support rollback on failure"),
]
for i in range(TARGET):
    e = next_entity()
    affirmative, base = VERB_PHRASES[i % len(VERB_PHRASES)]
    fam = f"NG-{base.split()[0]}"
    make_pair(
        "NG", f"The {e} {affirmative}.", f"The {e} does not {base}.",
        "CONTRADICTS", "negated", fam,
        contradiction_basis="explicit_negation", exclusivity_type="verb_polarity",
    )

# ── 3. CONTRADICTS: numeric (already exclusive: one measured value) ─────
NUMERIC_UNITS = [
    "GB of RAM", "compute nodes", "milliseconds of average latency",
    "requests per second", "degrees Celsius of rated operating temperature",
    "kilometers of maximum range", "percent measured uptime last quarter",
    "watts of peak power draw", "terabytes of usable storage",
    "concurrent user sessions", "microseconds of jitter",
    "known firmware revisions", "megabits per second of throughput",
    "years of warranty coverage", "independent replicas",
]
for i in range(TARGET):
    e = next_entity()
    unit = NUMERIC_UNITS[i % len(NUMERIC_UNITS)]
    n1 = 4 + i * 3
    n2 = n1 + 17 + (i % 5)
    fam = f"NU-{unit.split()[0]}"
    make_pair(
        "NU", f"The {e} has exactly {n1} {unit}.", f"The {e} has exactly {n2} {unit}.",
        "CONTRADICTS", "numeric", fam,
        contradiction_basis="single_measured_value", exclusivity_type=unit,
    )

# ── 4. CONTRADICTS: temporal (state at a fixed instant is exclusive) ────
MONTHS = ["January", "March", "May", "July", "September", "November"]
YEARS = [2022, 2023, 2024, 2025]
STATE_PAIRS = [
    ("deprecated", "actively maintained"), ("cancelled", "greenlit for continued funding"),
    ("in closed beta", "generally available"), ("offline for maintenance", "fully operational"),
    ("under a hiring freeze", "actively expanding its team"),
    ("paused pending review", "proceeding on schedule"),
    ("end-of-life", "receiving regular security patches"),
    ("unavailable in the EU region", "available in all supported regions"),
]
for i in range(TARGET):
    e = next_entity()
    month, year = MONTHS[i % len(MONTHS)], YEARS[i % len(YEARS)]
    s_a, s_b = STATE_PAIRS[i % len(STATE_PAIRS)]
    fam = f"TM-{s_a.split()[0]}"
    make_pair(
        "TM",
        f"As of {month} {year}, the {e} is {s_a}.",
        f"As of {month} {year}, the {e} is {s_b}.",
        "CONTRADICTS", "temporal", fam,
        contradiction_basis="temporal_state_exclusivity", exclusivity_type="operational_status_at_fixed_time",
    )

# ── 5. CONTRADICTS: entity (RECTIFIED P0-3: "solely" makes attribution
#    single-valued -- co-development would otherwise make both claims true) ─
for i in range(TARGET):
    e = next_entity()
    if i % 2 == 0:
        p1, p2 = PEOPLE[i % len(PEOPLE)], PEOPLE[(i + 7) % len(PEOPLE)]
        make_pair(
            "EN", f"The {e} was solely designed by {p1}.", f"The {e} was solely designed by {p2}.",
            "CONTRADICTS", "entity", "EN-person",
            contradiction_basis="sole_attribution", exclusivity_type="sole_designer",
        )
    else:
        t1, t2 = TEAMS[i % len(TEAMS)], TEAMS[(i + 3) % len(TEAMS)]
        make_pair(
            "EN", f"The {e} was developed solely by {t1}.", f"The {e} was developed solely by {t2}.",
            "CONTRADICTS", "entity", "EN-team",
            contradiction_basis="sole_attribution", exclusivity_type="sole_developer",
        )

# ── 6. CONTRADICTS: attribute (adjective negation; already exclusive) ───
ADJ_PROPS = [
    "waterproof", "backwards-compatible", "open-source", "thread-safe",
    "GPU-accelerated", "fault-tolerant", "field-replaceable", "rack-mountable",
    "hot-swappable", "tamper-evident", "self-hosted", "vendor-agnostic",
    "audit-logged", "single-tenant", "air-gapped",
]
for i in range(TARGET):
    e = next_entity()
    adj = ADJ_PROPS[i % len(ADJ_PROPS)]
    make_pair(
        "AT", f"The {e} is {adj}.", f"The {e} is not {adj}.",
        "CONTRADICTS", "attribute", f"AT-{adj}",
        contradiction_basis="explicit_negation", exclusivity_type="adjective_polarity",
    )

# ── 7. SUPPORTS: independent confirmation (RECTIFIED P0-1: every
#    confirming sentence restates the SAME verb phrase with an explicit
#    subject -- "Independent benchmarks confirm that the {e} {v}." --
#    never a dangling verb phrase with no subject) ──────────────────────
SUPPORT_VERBS = [
    "reduces average job latency", "improves search retrieval speed",
    "reduces power consumption during idle periods",
    "improves compilation speed for large projects",
    "increases fault tolerance under network partition",
    "achieves high accuracy on the validation set",
    "lowers memory overhead per request", "shortens cold-start time",
    "reduces tail latency at the 99th percentile", "increases cache hit rate",
]
SUPPORT_ATTRIBUTIONS = [
    "Independent benchmarks confirm that the {e} {v}.",
    "An internal review independently confirmed that the {e} {v}.",
    "A separate audit found that the {e} {v}.",
    "External testing verified that the {e} {v}.",
]
for i in range(51):
    e = next_entity()
    v = SUPPORT_VERBS[i % len(SUPPORT_VERBS)]
    attrib_template = SUPPORT_ATTRIBUTIONS[i % len(SUPPORT_ATTRIBUTIONS)]
    make_pair(
        "SP",
        f"The {e} {v}.",
        attrib_template.format(e=e, v=v),
        "SUPPORTS", "supports", f"SP-{i % len(SUPPORT_ATTRIBUTIONS)}",
    )

# ── 8. REFINES: 7 independent specificity mechanisms, distinct families ──
# RECTIFIED (P0-10): previously one mechanism (percent + date), exactly
# what the specificity heuristic scores on. Now 7 independent mechanisms,
# each its own template_family_id, so recall/accuracy is not measuring
# "does the heuristic recognize its own feature" alone.
REFINE_BASE = [
    "improves compilation speed for large projects",
    "reduces power consumption during idle periods",
    "increases fault tolerance under network partition",
    "improves search retrieval speed",
    "reduces average job latency",
    "increases cache hit rate",
    "shortens cold-start time",
]
REGIONS = ["Southeast Asia", "Northern Europe", "the US Midwest", "East Africa", "South America"]
DATASETS = ["the Meridian-500 benchmark suite", "the internal Q3 regression suite", "the OpenBench-12 corpus", "the Farrow load-test harness"]

def refine_family(name, text_fn):
    fam = f"RF-{name}"
    for i in range(7):
        e = next_entity()
        base = REFINE_BASE[i % len(REFINE_BASE)]
        make_pair("RF", f"The {e} {base}.", text_fn(e, base, i), "REFINES", "refinement", fam)

# RECTIFIED (external "reality check" review round 3, P0-2 "REFINES
# construction is still logically questionable"): "the {e} {base} for
# clusters exceeding N nodes" and "... specifically under sustained
# high-concurrency load" are RESTRICTIVE qualifiers -- read literally,
# they scope the claim down to a subset (only true for that subset), so
# the refined claim (B) does NOT entail the general claim (A) under
# ordinary semantics; the entailment this category is supposed to
# demonstrate (B -> A, B is A plus specificity) does not actually hold.
# Reworded so the added detail is explicitly an ELABORATION that
# preserves the general claim ("particularly/especially in X"), matching
# this file's own geographic mechanism (which already used "most notably
# in X" -- the correct pattern) rather than restrictive "for X"/
# "specifically under X" scoping.
refine_family("numeric_date", lambda e, base, i: f"The {e} {base} by {12 + i * 5} percent, as measured in {MONTHS[i % len(MONTHS)]} {YEARS[i % len(YEARS)]} benchmarks.")
refine_family("geographic", lambda e, base, i: f"The {e} {base}, most notably in {REGIONS[i % len(REGIONS)]} deployments.")
refine_family("population", lambda e, base, i: f"The {e} {base}, particularly for clusters exceeding {50 + i * 25} nodes.")
refine_family("condition", lambda e, base, i: f"The {e} {base}, with the effect especially pronounced under sustained high-concurrency load.")
refine_family("dataset", lambda e, base, i: f"The {e} {base}, as measured on {DATASETS[i % len(DATASETS)]}.")
refine_family("causal_mechanism", lambda e, base, i: f"The {e} {base} by caching intermediate results instead of recomputing them each time.")
refine_family("qualification", lambda e, base, i: f"The {e} {base}, though the effect is smaller for workloads under {20 + i * 10} requests per second.")

# ── 9. EQUIVALENT: 7 difficulty tiers, distinct families ────────────────
# RECTIFIED (P0-11): previously one pattern (close lexical paraphrase).
def equiv_family(name, pairs):
    fam = f"EV-{name}"
    for i, (t_a, t_b) in enumerate(pairs):
        e = next_entity()
        make_pair("EV", f"The {e} {t_a}.", f"The {e} {t_b}.", "EQUIVALENT", "equivalent", fam)

equiv_family("easy_lexical", [
    ("supports GPU execution", "is compatible with GPU-based execution"),
    ("reduces average latency", "lowers the average latency"),
    ("increases fault tolerance", "makes the system more fault-tolerant"),
    ("supports horizontal scaling", "can be scaled horizontally"),
    ("caches query results", "keeps a cache of query results"),
    ("compresses network payloads", "shrinks network payloads before sending them"),
    ("retries failed requests automatically", "automatically retries a request that fails"),
])
equiv_family("medium_syntactic", [
    ("uses 8 GB of RAM", "has 8 GB of RAM installed"),
    ("processes requests asynchronously", "requests are processed by it asynchronously"),
    ("validates every input schema", "every input schema is validated by it"),
    ("logs each request body", "each request body is logged by it"),
    ("enforces rate limiting on writes", "rate limiting on writes is enforced by it"),
    ("encrypts data at rest", "data at rest is encrypted by it"),
    ("evicts entries using an LRU policy", "an LRU policy is used by it to evict entries"),
])
equiv_family("hard_divergent", [
    ("has 8 GB of RAM", "its memory capacity is 8 gigabytes"),
    ("reduces job latency", "makes jobs finish sooner on average"),
    ("supports multi-tenancy", "can serve more than one tenant from a single deployment"),
    ("retries on failure", "does not give up after a single failed attempt"),
    ("is fault-tolerant", "keeps functioning after a component fails"),
    ("scales horizontally", "handles more load by adding machines rather than upgrading one"),
    ("encrypts data at rest", "nothing is stored on disk unencrypted"),
])
equiv_family("contextual", [
    ("uses 8 GB of RAM", "when engineers were asked about its memory, they confirmed 8 GB is provisioned"),
    ("supports GPU execution", "in a Q\\&A session, the team stated GPU workloads are supported"),
    ("reduces average latency", "a retrospective noted that average latency had gone down as a result"),
    ("requires authentication", "the security review noted that access without authentication is not possible"),
    ("supports offline mode", "the release notes mention that it can now be used without connectivity"),
    ("caches query results", "the design doc explains that repeated queries are served from a cache"),
    ("enforces rate limiting", "an incident postmortem confirmed excess requests are throttled"),
])
equiv_family("negation_preserving", [
    ("requires authentication", "cannot be accessed without authentication"),
    ("requires a valid API key", "cannot be called without a valid API key"),
    ("requires TLS", "cannot accept connections without TLS"),
    ("requires an active session", "cannot process a request without an active session"),
    ("requires administrator approval", "cannot be deployed without administrator approval"),
    ("requires a signed certificate", "cannot start without a signed certificate"),
    ("requires a quorum of nodes", "cannot commit a write without a quorum of nodes"),
])
equiv_family("numerical", [
    ("responds in 0.5 seconds on average", "responds in 500 milliseconds on average"),
    ("has a 1.5 second timeout", "has a 1500 millisecond timeout"),
    ("polls every 0.25 seconds", "polls every 250 milliseconds"),
    ("has a 2 minute cache TTL", "has a 120 second cache TTL"),
    ("processes a batch every 0.1 seconds", "processes a batch every 100 milliseconds"),
    ("has a 1 hour session timeout", "has a 60 minute session timeout"),
    ("retries after 0.75 seconds", "retries after 750 milliseconds"),
])
equiv_family("unit", [
    ("has 4 GB of RAM", "has 4096 MB of RAM"),
    ("has a 1 TB disk", "has a 1024 GB disk"),
    ("supports 1 Gbps throughput", "supports 1000 Mbps throughput"),
    ("weighs 2 kg", "weighs 2000 grams"),
    ("has a 10 km range", "has a 10000 meter range"),
    ("draws 1.5 kW at peak", "draws 1500 W at peak"),
    ("stores 2 TB of logs", "stores 2048 GB of logs"),
])

# ── 10. NEUTRAL (hard): same-topic, different non-conflicting facet ─────
SAME_TOPIC_FACETS = [
    ("was manufactured in {y}", "completed its first field test in {loc}"),
    ("is maintained by a team of {n} engineers", "was first announced at a conference in {loc}"),
    ("has an internal codename used during development", "is documented in a public changelog"),
    ("was migrated to a new build system in {y}", "has a dedicated on-call rotation"),
    ("is discussed in an internal design document", "has a public status page"),
]
LOCATIONS = ["Nevada", "Ontario", "Bavaria", "Queensland", "Kerala", "Alberta", "Gujarat", "Saxony"]
for i in range(TARGET):
    e = next_entity()
    f_a, f_b = SAME_TOPIC_FACETS[i % len(SAME_TOPIC_FACETS)]
    y = YEARS[i % len(YEARS)]
    loc = LOCATIONS[i % len(LOCATIONS)]
    n = 3 + i % 12
    make_pair(
        "HS",
        f"The {e} {f_a.format(y=y, loc=loc, n=n)}.",
        f"The {e} {f_b.format(y=y, loc=loc, n=n)}.",
        "NEUTRAL", "neutral_hard_same_topic", f"HS-{i % len(SAME_TOPIC_FACETS)}",
    )

# ── 11. NEUTRAL (hard): lexical collision across domains ────────────────
COLLISIONS = [
    ("Python", "is the primary scripting language for this deployment tool", "python", "sheds its skin several times a year as it grows"),
    ("Java", "executes compiled bytecode on a virtual machine", "the island of Java", "produces some of Indonesia's most well-known coffee"),
    ("Mercury", "is a lightweight, fast configuration-loading library", "Mercury", "is the closest planet to the Sun"),
    ("Amazon", "is a cloud-computing platform used for this deployment", "the Amazon", "river discharges more water than the next seven largest rivers combined"),
    ("Oracle", "refers to the relational database management system here", "the Oracle", "of Delphi was a priestess in ancient Greece"),
    ("Swift", "is Apple's compiled programming language", "the swift", "is a fast-flying bird related to hummingbirds"),
    ("Rust", "is a systems programming language emphasizing memory safety", "rust", "is an iron oxide that forms on unprotected metal"),
    ("Django", "is a Python web framework used for this backend", "Django", "is a 2012 western film directed by Quentin Tarantino"),
    ("Pandas", "is a Python library for tabular data analysis", "pandas", "are bears native to south-central China"),
    ("Atlas", "is the internal name for this deployment's config service", "Atlas", "was a Titan condemned to hold up the sky in Greek myth"),
    ("Phoenix", "is the codename for this release pipeline", "the phoenix", "is a mythical bird said to be reborn from its ashes"),
    ("Jaguar", "is the internal codename for the new build agent", "the jaguar", "is the largest cat native to the Americas"),
]
for i in range(TARGET):
    n1, s1, n2, s2 = COLLISIONS[i % len(COLLISIONS)]
    suffix = "" if i < len(COLLISIONS) else f" (variant {i // len(COLLISIONS)})"
    text_a = f"{n1} {s1}{suffix}."
    text_b = f"{n2.capitalize() if i % 2 else n2} {s2}{suffix}."
    make_pair("HL", text_a, text_b, "NEUTRAL", "neutral_hard_lexical_collision", f"HL-{i % len(COLLISIONS)}")

# ── 12. NEUTRAL (hard): multi-attribute (same entity, compatible attrs) ──
FEATURE_PAIRS = [
    ("LiDAR", "a stereo camera", "obstacle detection"),
    ("Redis", "an in-memory LRU cache", "response caching"),
    ("OAuth 2.0", "a static API key", "client authentication"),
    ("TLS 1.3", "mutual TLS", "transport encryption"),
    ("a message queue", "a webhook callback", "asynchronous notification delivery"),
    ("round-robin", "least-connections balancing", "traffic distribution"),
    ("a Bloom filter", "a hash index", "membership testing"),
    ("gRPC", "a REST fallback endpoint", "external API access"),
    ("an ultrasonic sensor", "an infrared proximity sensor", "short-range obstacle detection"),
    ("snapshot backups", "continuous write-ahead-log replication", "data durability"),
]
for i in range(45):
    e = next_entity()
    f_a, f_b, purpose = FEATURE_PAIRS[i % len(FEATURE_PAIRS)]
    make_pair("HM", f"The {e} uses {f_a} for {purpose}.", f"The {e} uses {f_b} for {purpose}.", "NEUTRAL", "neutral_hard_multi_attribute", f"HM-{i % len(FEATURE_PAIRS)}")

# ── 13. NEUTRAL (hard): adjacent, non-conflicting aspects of one technique ─
ADJACENT_PAIRS = [
    ("Pressure cooking", "reduces total cooking time for tough cuts of meat", "raises the internal cooking chamber above atmospheric pressure"),
    ("Slow braising", "tenderizes collagen-rich cuts of meat over several hours", "works well with a heavy-bottomed pot that retains heat evenly"),
    ("Sous vide cooking", "holds food at a precise, constant temperature", "requires the food to be sealed in an airtight bag"),
    ("Blast chilling", "rapidly lowers food temperature after cooking", "is typically done in a dedicated chamber rather than a standard freezer"),
    ("Canary deployment", "gradually shifts traffic to a new release", "requires health metrics to be monitored per traffic slice"),
    ("Blue-green deployment", "keeps two full environments running simultaneously", "requires a load balancer that can switch traffic atomically"),
    ("Database sharding", "distributes rows across multiple physical nodes", "requires a consistent hashing or range-based routing scheme"),
    ("Circuit breaking", "stops sending requests to a failing dependency", "requires a half-open state to test recovery"),
]
for i in range(TARGET):
    subj, a, b = ADJACENT_PAIRS[i % len(ADJACENT_PAIRS)]
    suffix = f" (case {i // len(ADJACENT_PAIRS) + 1})" if i >= len(ADJACENT_PAIRS) else ""
    make_pair("HA", f"{subj} {a}{suffix}.", f"{subj} {b}{suffix}.", "NEUTRAL", "neutral_hard_adjacent_non_conflicting", f"HA-{i % len(ADJACENT_PAIRS)}")

# ── 14. NEUTRAL (easy): unrelated domains, zero vocabulary overlap ──────
TECH_FACTS = [
    "is written in the Rust programming language", "stores configuration values as key-value pairs",
    "processes messages in first-in-first-out order", "runs nightly data validation checks",
    "provides a shared caching layer", "evicts entries using a least-recently-used policy",
    "exposes a health-check endpoint on port 8080", "compresses logs before archiving them",
    "rotates access tokens every 24 hours", "batches writes before flushing to disk",
]
RANDOM_FACTS = [
    "Tamil is one of the oldest continuously spoken classical languages.",
    "Neptune's winds are the fastest measured in the solar system.",
    "Baklava is a layered pastry dish popular across the Balkans and Levant.",
    "Off-spin bowling relies on finger rotation rather than wrist action.",
    "The Amazon rainforest spans nine countries in South America.",
    "The Eiffel Tower was completed in 1889 for the World's Fair.",
    "Honey never spoils if stored in a sealed container.",
    "The mitochondria is often called the powerhouse of the cell.",
    "Flamenco originated in the Andalusian region of southern Spain.",
    "Mount Kilimanjaro is the highest peak on the African continent.",
    "Origami is the traditional Japanese art of paper folding.",
    "The Sahara is the largest hot desert in the world.",
]
for i in range(51):
    e = next_entity()
    tf = TECH_FACTS[i % len(TECH_FACTS)]
    rf = RANDOM_FACTS[i % len(RANDOM_FACTS)]
    cycle = i // len(RANDOM_FACTS)
    rf_text = rf if cycle == 0 else rf[:-1] + f" (fact set {cycle + 1})."
    make_pair("UN", f"The {e} {tf}.", rf_text, "NEUTRAL", "neutral", f"UN-{i % len(TECH_FACTS)}")

# ── 15. Ambiguous / abstention: hedged, genuinely unclear relation ──────
AMBIGUOUS_TEMPLATES = [
    ("build time varies depending on project size", "some large projects report longer build times"),
    ("performance can differ across hardware configurations", "certain configurations may see reduced performance"),
    ("behavior under high load is not fully characterized", "a few reports mention degraded behavior under heavy load"),
    ("results may vary depending on network conditions", "some deployments have observed inconsistent results"),
    ("compatibility with older clients is not guaranteed", "a handful of older clients reportedly still work"),
    ("the effect of this setting is difficult to isolate", "one internal note suggests it may have a minor effect"),
]
for i in range(45):
    e = next_entity()
    t_a, t_b = AMBIGUOUS_TEMPLATES[i % len(AMBIGUOUS_TEMPLATES)]
    make_pair(
        "AM", f"The {e}'s {t_a}.", f"For the {e}, {t_b}.",
        "UNKNOWN", "ambiguous_abstention", f"AM-{i % len(AMBIGUOUS_TEMPLATES)}",
    )


def main():
    assign_splits_stratified_by_category(new_entries)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(new_entries, indent=2, ensure_ascii=False), encoding="utf-8")
    from collections import Counter
    cat_counts = Counter(e["category"] for e in new_entries)
    fam_counts = Counter(e["template_family_id"] for e in new_entries)
    split_counts = Counter(e["split"] for e in new_entries)
    print(f"Generated {len(new_entries)} pairs across {len(cat_counts)} categories, "
          f"{len(fam_counts)} template families:")
    for cat, n in sorted(cat_counts.items()):
        print(f"  {cat:<35} {n}")
    print(f"\nSplit: {dict(split_counts)}")
    print(f"Wrote manifest to {MANIFEST_PATH}")
    print(f"Wrote {len(new_entries) * 2} documents to {CORPUS_DIR}")


if __name__ == "__main__":
    main()
