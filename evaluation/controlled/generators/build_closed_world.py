"""
build_closed_world.py -- SMRITI-ClosedWorld-v1: a closed LABELED-PAIR
benchmark (P0-8, "PLEASE FIX AND SAVE ME" review round; terminology
corrected P0-D, "FINAL REVIEW" round -- this is NOT a fully closed
candidate-UNIVERSE benchmark, see the note at the end of this docstring).

Motivation: SMRITI-Controlled-v2's own candidate-level numbers
(evaluation/controlled/v2/results.json's candidate_metrics,
paper/sections/controlled_results.tex finding 6) are OPEN-WORLD: Phase 6
is run with every NLI-scored candidate retained, and any candidate pair
outside the 713-pair manifest is reported as a volume count, explicitly
NOT a false-positive count, because we have no gold label for pairs the
corpus never intended to test -- they might be genuine, uncatalogued
contradictions. That is an honest limitation, not a bug, but it means
"candidate precision" in the conventional sense (true/false positive
rate against a KNOWN answer) has never actually been measured for
SMRITI's candidate-retrieval + CONTRADICTS-classification pipeline.

This benchmark closes that gap for CONTRADICTS specifically (the
relation type the open-world measurement flagged as having the largest
unaudited volume) by constructing 900 DESIGNATED pairs (1,800 documents)
where every one of those 900 has a known true label:

  (A) 300 "intended" pairs -- a stratified sample of SMRITI-Controlled-v2's
      own core-semantic-relations pairs (already validated by
      validate_corpus.py), copied verbatim (same doc IDs, same text,
      same expected_relation/expected_status) into this benchmark's own
      corpus directory so it is fully self-contained and does not depend
      on data/raw/controlled_v2 being present.

  (B) 300 "guaranteed_neutral_distractor" pairs -- fresh entities, two
      DIFFERENT non-conflicting attributes from the same orthogonal pool
      controlled-v2's CONTRADICTS "direct" subtype uses (e.g. "primary
      deployment platform" vs. "default network protocol") applied to
      the SAME entity. Lexically and structurally close to a genuine
      CONTRADICTS pair (same sentence template, same entity, same
      attribute-is-X phrasing) -- exactly the kind of pair embedding
      retrieval would plausibly surface as a candidate -- but NEUTRAL by
      construction: two orthogonal attributes of one entity are not in
      tension. If the resolver calls CONTRADICTS on one of these, that
      is now a provable false positive, not an open-world "volume count".

  (C) 300 "guaranteed_contradiction_distractor" pairs -- fresh entities,
      the SAME validated single-valued-attribute CONTRADICTS construction
      as controlled-v2's "direct" subtype (contradiction_basis=
      "single_valued_attribute"), but NOT part of bucket (A)'s "intended"
      membership. These test whether the open-world measurement's
      "out-of-manifest CONTRADICTS calls" are typically genuine
      contradictions the corpus simply never catalogued (the honest
      reading finding 6 already gives them) or resolver errors: a
      construction identical to a already-validated CONTRADICTS subtype,
      scored outside its own manifest's bookkeeping, should still be
      called CONTRADICTS if the resolver is behaving consistently.

Do NOT read this benchmark as validating SUPPORTS/REFINES/EQUIVALENT
closed labeled-pair precision -- bucket (A) carries those labels forward
for corpus completeness, but buckets (B)/(C) are both CONTRADICTS-vs-NEUTRAL
distractors by design, matching the specific open-world gap this
benchmark exists to close.

RECTIFIED (P0-D, "FINAL REVIEW" round -- terminology correction): this
is a closed LABELED-PAIR benchmark, not a closed candidate-UNIVERSE
benchmark. The 900 pairs above are closed (every one has a known true
label), but the 1,800-document pool they live in is not: Phase 6
actually scores far more candidates within that document set than just
these 900 (score_closed_world.py reports the exact count), and every one
of those additional candidates carries no known label at all. Precision/
recall/F1 computed here are real and checkable ON THE 900 DESIGNATED
PAIRS, not a true closed-world measurement over the complete candidate
universe those 1,800 documents can generate -- that would require a
benchmark where every possible pair among a small claim set is
labelable by construction (e.g. ~100 claims, all ~4,950 pairs labeled),
which this benchmark is not and does not claim to be.

Run with: poetry run python evaluation/controlled/generators/build_closed_world.py
"""
import itertools
import json
import random
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE_CORPUS_DIR = ROOT / "data" / "raw" / "controlled_v2"
SOURCE_MANIFEST_PATH = ROOT / "evaluation" / "controlled" / "v2" / "construction_manifest.json"
CORPUS_DIR = ROOT / "data" / "raw" / "closed_world_v1"
MANIFEST_PATH = ROOT / "evaluation" / "closed_world" / "v1" / "construction_manifest.json"

random.seed(20260911911)
CORPUS_DIR.mkdir(parents=True, exist_ok=True)
MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)

CORE_CATEGORIES = {
    "direct", "negated", "numeric", "temporal", "entity", "attribute",
    "supports", "refinement", "equivalent", "neutral",
}
TARGET_INTENDED = 300
TARGET_DISTRACTOR = 300

# ── Fresh entity pool, disjoint in spelling from controlled_v2's NAME_A/B
#    (own vocabulary so a reader auditing this benchmark's corpus
#    directory sees at a glance which pairs are new vs. copied) ──────────
CW_NAME_A = [
    "Basalt", "Coriander", "Driftwood", "Ebonrise", "Foxglove", "Granwick",
    "Hollowmere", "Inkstone", "Jarrowfield", "Kettlebrook", "Lanternhold",
    "Mossgate", "Netherwell", "Oxhollow", "Pinecrest", "Quarrywood",
    "Redshale", "Slatemoor", "Timberlynn", "Urnfield", "Violetcairn",
    "Wickerham", "Yarrowdale", "Zephyrgate", "Ashendell", "Briarcombe",
    "Cloverwick", "Duskhaven", "Elmshadow", "Frostgale",
]
CW_NAME_B = [
    "Broker", "Collector", "Dispatcher", "Emitter", "Forwarder",
    "Handler", "Interpreter", "Journal", "Loader", "Mapper", "Notifier",
    "Orchestrator", "Parser", "Reducer", "Sampler", "Tracker",
    "Validator", "Watcher", "Extractor", "Synchronizer",
]
_cw_combos = list(itertools.product(CW_NAME_A, CW_NAME_B))
random.shuffle(_cw_combos)
_cw_entity_iter = iter(_cw_combos)


def next_cw_entity() -> str:
    a, b = next(_cw_entity_iter)
    return f"{a} {b}"


_written_texts = set()
new_entries = []
_id_counters = {}


def register(text: str) -> str:
    if text and text[0].islower():
        text = text[0].upper() + text[1:]
    if text in _written_texts:
        raise ValueError(f"Duplicate generated text in closed-world benchmark: {text!r}")
    _written_texts.add(text)
    return text


def make_pair(prefix, text_a, text_b, expected_relation, bucket, category,
              contradiction_basis=None, exclusivity_type=None):
    text_a = register(text_a)
    text_b = register(text_b)
    n = _id_counters.get(prefix, 0) + 1
    _id_counters[prefix] = n
    doc_a, doc_b = f"{prefix}{n:03d}a", f"{prefix}{n:03d}b"
    (CORPUS_DIR / f"{doc_a}.md").write_text(f"# {doc_a}\n\n{text_a}\n", encoding="utf-8")
    (CORPUS_DIR / f"{doc_b}.md").write_text(f"# {doc_b}\n\n{text_b}\n", encoding="utf-8")
    entry = {
        "doc_a": doc_a, "text_a": text_a,
        "doc_b": doc_b, "text_b": text_b,
        "expected_relation": expected_relation,
        "expected_status": "RESOLVED",
        "direction": None,
        "bucket": bucket,
        "category": category,
        "label_provenance": "CONSTRUCTION_DEFINED",
    }
    if contradiction_basis:
        entry["contradiction_basis"] = contradiction_basis
    if exclusivity_type:
        entry["exclusivity_type"] = exclusivity_type
    new_entries.append(entry)


def stratified_sample(manifest, categories, target_total, seed_rng):
    """Proportional allocation across categories, largest-remainder method
    so the per-category counts sum EXACTLY to target_total."""
    by_cat = {}
    for e in manifest:
        if e["category"] in categories:
            by_cat.setdefault(e["category"], []).append(e)
    total_available = sum(len(v) for v in by_cat.values())
    raw = {cat: len(v) * target_total / total_available for cat, v in by_cat.items()}
    floor_counts = {cat: int(r) for cat, r in raw.items()}
    remainder = target_total - sum(floor_counts.values())
    remainders = sorted(raw.items(), key=lambda kv: kv[1] - int(kv[1]), reverse=True)
    for cat, _ in remainders[:remainder]:
        floor_counts[cat] += 1
    sampled = []
    for cat, entries in by_cat.items():
        entries_sorted = sorted(entries, key=lambda e: e["doc_a"])
        seed_rng.shuffle(entries_sorted)
        sampled.extend(entries_sorted[: floor_counts[cat]])
    return sampled


# ── (A) 300 "intended" pairs: stratified sample of controlled-v2's own
#     validated core-semantic-relations pairs, copied verbatim ──────────
source_manifest = json.loads(SOURCE_MANIFEST_PATH.read_text(encoding="utf-8"))
intended_sample = stratified_sample(
    source_manifest, CORE_CATEGORIES, TARGET_INTENDED, random.Random(20260911)
)
assert len(intended_sample) == TARGET_INTENDED, f"got {len(intended_sample)}"

for e in intended_sample:
    for doc_id in (e["doc_a"], e["doc_b"]):
        src = SOURCE_CORPUS_DIR / f"{doc_id}.md"
        dst = CORPUS_DIR / f"{doc_id}.md"
        shutil.copyfile(src, dst)
    _written_texts.add(e["text_a"])
    _written_texts.add(e["text_b"])
    entry = {
        "doc_a": e["doc_a"], "text_a": e["text_a"],
        "doc_b": e["doc_b"], "text_b": e["text_b"],
        "expected_relation": e["expected_relation"],
        "expected_status": e["expected_status"],
        "direction": e.get("direction"),
        "bucket": "intended",
        "category": e["category"],
        "label_provenance": "CONSTRUCTION_DEFINED",
        "source": "controlled_v2",
    }
    if "contradiction_basis" in e:
        entry["contradiction_basis"] = e["contradiction_basis"]
    if "exclusivity_type" in e:
        entry["exclusivity_type"] = e["exclusivity_type"]
    new_entries.append(entry)

# ── (B) 300 guaranteed_neutral_distractor pairs: two DIFFERENT orthogonal
#     attributes of the SAME entity -- lexically close to a CONTRADICTS
#     "direct" pair, but not in tension ──────────────────────────────────
ATTR_VALUE_POOL = [
    ("primary deployment platform", ["ARM64", "x86-64", "RISC-V"]),
    ("default network protocol", ["IPv4", "IPv6", "QUIC"]),
    ("primary storage backend", ["a relational store", "a document store", "an object store"]),
    ("primary hosting region", ["the eastern region", "the western region", "the northern region"]),
    ("primary execution environment", ["bare metal", "virtual machines", "containers"]),
    ("default billing tier", ["the free tier", "the enterprise tier", "the standard tier"]),
    ("default provisioning mode", ["spot instances", "reserved instances", "on-demand instances"]),
    ("primary authentication method", ["API keys", "OAuth tokens", "signed certificates"]),
]
_attr_pairs = [
    (i, j) for i in range(len(ATTR_VALUE_POOL)) for j in range(len(ATTR_VALUE_POOL)) if i != j
]
for i in range(TARGET_DISTRACTOR):
    e = next_cw_entity()
    ai, aj = _attr_pairs[i % len(_attr_pairs)]
    attr_a, values_a = ATTR_VALUE_POOL[ai]
    attr_b, values_b = ATTR_VALUE_POOL[aj]
    val_a = values_a[i % len(values_a)]
    val_b = values_b[(i + 1) % len(values_b)]
    make_pair(
        "CWN",
        f"The {e}'s {attr_a} is {val_a}.",
        f"The {e}'s {attr_b} is {val_b}.",
        "NEUTRAL", "guaranteed_neutral_distractor", "guaranteed_neutral_distractor",
    )

# ── (C) 300 guaranteed_contradiction_distractor pairs: same validated
#     single-valued-attribute construction as controlled-v2's "direct"
#     CONTRADICTS subtype, fresh entities, outside the intended manifest ─
for i in range(TARGET_DISTRACTOR):
    e = next_cw_entity()
    attr, values = ATTR_VALUE_POOL[i % len(ATTR_VALUE_POOL)]
    val_a = values[i % len(values)]
    val_b = values[(i + 1) % len(values)]
    make_pair(
        "CWC",
        f"The {e}'s {attr} is {val_a}.",
        f"The {e}'s {attr} is {val_b}.",
        "CONTRADICTS", "guaranteed_contradiction_distractor", "guaranteed_contradiction_distractor",
        contradiction_basis="single_valued_attribute", exclusivity_type=attr,
    )

assert len(new_entries) == TARGET_INTENDED + 2 * TARGET_DISTRACTOR, len(new_entries)

MANIFEST_PATH.write_text(json.dumps(new_entries, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Wrote {len(new_entries)} pairs ({2 * len(new_entries)} documents) to {CORPUS_DIR}")
print(f"Manifest: {MANIFEST_PATH}")
from collections import Counter
print("Bucket counts:", Counter(e["bucket"] for e in new_entries))
