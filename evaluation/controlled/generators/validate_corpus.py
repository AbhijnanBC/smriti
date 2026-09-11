"""
validate_corpus.py — CI-style gate for SMRITI-Controlled-v2.

RECTIFIED (external "reality check" review, P0-1): a prior generation
round produced a 707-pair corpus with ungrammatical negation
("does not supports"), subject-dropped SUPPORTS sentences, cross-category
duplicate propositions, and CONTRADICTS pairs whose two claims could both
be true simultaneously (no logical exclusivity premise). None of these
were caught before the corpus was used to report resolver accuracy
numbers. This script checks every pair in the manifest against exactly
the failure patterns the review named, and exits non-zero if any of them
appear -- run it after any corpus regeneration, before scoring against it.

Run with: python validate_corpus.py [manifest_path]
"""
import ast
import itertools
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MANIFEST = ROOT / "evaluation" / "controlled" / "v2" / "construction_manifest.json"
GENERATOR_PATH = Path(__file__).resolve().parent / "build_controlled_v2.py"

# "does not" / "did not" / "cannot" followed by a third-person-singular
# verb form (ends in -s, not "does"/"has"/"was"/"is" themselves) is the
# exact grammar defect this review found: negation must use the base
# form of the verb, not the inflected one.
_BAD_NEGATION_RE = re.compile(
    r"\b(does|did)\s+not\s+(\w+s)\b", re.IGNORECASE
)
_ALLOWED_ENDING_IN_S_AFTER_NEGATION = {
    "has", "was", "is", "this", "focus", "less", "process", "status",
    "compress", "address", "access", "assess", "express", "possess",
}

# A sentence opening with a bare present/past-tense verb (no subject
# before it) after a leading capitalized attribution clause is the
# "confirm that <verb phrase with no subject>" defect. Heuristic: the
# word immediately after "that " (or "confirm ", "found ", "verified ")
# should not itself be a bare third-person-singular verb form typically
# used without an explicit subject noun/pronoun directly before it.
_DANGLING_CONFIRM_RE = re.compile(
    r"\b(confirm(?:ed)?|found|verified)\s+that\s+(reduces|increases|improves|lowers|shortens|supports|requires|encrypts|allows|retries|validates|caches|logs|enforces|compresses)\b",
    re.IGNORECASE,
)

# RECTIFIED (external "reality check" review round 3, P0-1/P0-11): the
# "direct" CONTRADICTS category previously paired an attribute with a
# value from the WRONG domain (attribute/value lists indexed
# independently -- see build_controlled_v2.py's own fix note) --
# grammatical, but not a valid domain proposition. This checks that every
# "direct" pair's declared exclusivity_type (the attribute) is a known
# one, and that its two claim texts each mention one of that specific
# attribute's two permitted values -- catching a reintroduction of the
# same class of bug, not just today's specific instance of it.
_KNOWN_DIRECT_ATTR_VALUES = {
    "primary deployment platform": {"ARM64", "x86-64", "Linux", "Windows"},
    "default network protocol": {"IPv4", "IPv6"},
    "primary storage backend": {"a relational store", "a document store"},
    "primary hosting region": {"the eastern region", "the western region"},
    "primary execution environment": {"bare metal", "virtual machines"},
    "default billing tier": {"the free tier", "the enterprise tier"},
    "default provisioning mode": {"spot instances", "reserved instances"},
}

# RECTIFIED (P0-2): a REFINES pair's specific claim (text_b) must not use
# a RESTRICTIVE qualifier ("for X exceeding N", "specifically under X")
# without an immediately preceding preserving word ("particularly",
# "especially") -- restrictive phrasing scopes the claim DOWN to a
# subset, breaking the entailment REFINES requires. Fixed-width lookbehind
# (Python re supports this, unlike variable-width) checks the preserving
# word is directly adjacent, not merely present somewhere in the sentence.
# This is a regression guard for exactly the two bad phrasings this
# review found and fixed, not a general restrictive-language detector.
_RESTRICTIVE_REFINES_RE = re.compile(
    r"(?<!particularly )(?<!especially )\bfor\s+\w+\s+exceeding\b"
    r"|\bspecifically\s+under\b",
    re.IGNORECASE,
)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower()).rstrip(".")


def check_bad_negation(text: str) -> bool:
    for m in _BAD_NEGATION_RE.finditer(text):
        verb = m.group(2).lower()
        if verb not in _ALLOWED_ENDING_IN_S_AFTER_NEGATION:
            return True
    return False


def check_dangling_subject(text: str) -> bool:
    return bool(_DANGLING_CONFIRM_RE.search(text))


def check_restrictive_refines_scoping(text: str) -> bool:
    return bool(_RESTRICTIVE_REFINES_RE.search(text))


def check_direct_attribute_value_mismatch(entry: dict) -> str | None:
    """
    For a "direct" CONTRADICTS pair whose exclusivity_type is one of
    build_controlled_v2.py's own known attributes, verify that text_a/
    text_b each mention one of that attribute's two permitted values (and
    not the same one twice). Corpora using a different attribute
    vocabulary (e.g. the v1 pilot's "measured_quantity"-style pairs,
    already validated by their own construction) are silently skipped --
    this check only guards the specific v2-generator vocabulary this
    review's P0-1 fix applies to, not a universal domain ontology.
    Returns an error string, or None if the pair is consistent or the
    attribute is outside this check's known vocabulary.
    """
    attr = entry.get("exclusivity_type")
    if attr not in _KNOWN_DIRECT_ATTR_VALUES:
        return None
    allowed = _KNOWN_DIRECT_ATTR_VALUES[attr]
    text_a, text_b = entry["text_a"], entry["text_b"]
    value_a = next((v for v in allowed if v in text_a), None)
    value_b = next((v for v in allowed if v in text_b), None)
    if value_a is None:
        return f"text_a does not mention any permitted value of {attr!r}: {text_a!r}"
    if value_b is None:
        return f"text_b does not mention any permitted value of {attr!r}: {text_b!r}"
    if value_a == value_b:
        return f"text_a and text_b mention the SAME value of {attr!r} ({value_a!r}) -- not exclusive"
    return None


def _load_entity_name_pool() -> list[str]:
    """
    RECTIFIED (P1-E, "FINAL REVIEW" round): read build_controlled_v2.py's
    NAME_A/NAME_B literal lists via AST rather than importing the module
    -- importing it re-executes its top-level generation code and
    rewrites the corpus files as a side effect, which a read-only
    validator must never do. Returns every "{a} {b}" combination the
    generator's next_entity() can draw from (order doesn't matter here,
    only membership).
    """
    src = GENERATOR_PATH.read_text(encoding="utf-8")
    tree = ast.parse(src)
    pools = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id in ("NAME_A", "NAME_B"):
                pools[node.targets[0].id] = ast.literal_eval(node.value)
    if "NAME_A" not in pools or "NAME_B" not in pools:
        return []
    return [f"{a} {b}" for a, b in itertools.product(pools["NAME_A"], pools["NAME_B"])]


# RECTIFIED (P1-E): categories that do NOT draw from the shared NAME_A/
# NAME_B entity pool -- each instead fixes one subject per
# template_family_id by construction (e.g. family "HL-3" always uses
# COLLISIONS[3]'s subject, never any other). For these, template_family_id
# already IS a valid entity-disjointness key: two pairs share a subject
# iff they share a family, and family-level split assignment already
# keeps that subject on one side of dev/test. No text-parsing needed.
_FAMILY_IS_ENTITY_KEY_CATEGORIES = {
    "neutral_hard_lexical_collision",
    "neutral_hard_adjacent_non_conflicting",
}


def extract_entity_key(entry: dict, entity_pool: list[str]) -> str | None:
    """
    RECTIFIED (P1-E, "FINAL REVIEW" round): best-effort reconstruction of
    which "entity" (the fictional company/product name build_controlled_v2.py
    draws via next_entity(), e.g. "Emberfen Queue") a pair is about, so
    dev/test can be checked for entity leakage in addition to template-
    family leakage (the external review's finding: "the split is
    template-family-disjoint but not entity-disjoint"). Returns None for
    a pair whose category uses neither mechanism this function knows
    about (currently: none -- every category either draws from the
    NAME_A/NAME_B pool or fixes one subject per family; a future category
    that does neither would fall through to None and be excluded from
    the entity-disjointness check, not silently misreported).
    """
    if entry.get("category") in _FAMILY_IS_ENTITY_KEY_CATEGORIES:
        return entry.get("template_family_id")
    for combo in entity_pool:
        if combo in entry["text_a"] or combo in entry["text_b"]:
            return combo
    return None


def validate(manifest_path: Path) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors = []
    seen_exact = {}
    seen_normalized = {}
    seen_semantic_instance = {}  # (category, family, normalized-with-entity-stripped) -> first doc

    for entry in manifest:
        for side in ("a", "b"):
            doc = entry[f"doc_{side}"]
            text = entry[f"text_{side}"]

            if check_bad_negation(text):
                errors.append(f"[grammar] {doc}: 'does/did not' + inflected verb: {text!r}")
            if check_dangling_subject(text):
                errors.append(f"[grammar] {doc}: dangling-subject confirmation clause: {text!r}")
            if not re.match(r"^[A-Z0-9\"']", text.strip()):
                errors.append(f"[grammar] {doc}: does not start with a capital letter/subject: {text!r}")

            if text in seen_exact:
                errors.append(f"[duplicate-exact] {doc} duplicates {seen_exact[text]}: {text!r}")
            else:
                seen_exact[text] = doc

            norm = _normalize(text)
            if norm in seen_normalized and seen_normalized[norm] != seen_exact.get(text):
                errors.append(f"[duplicate-normalized] {doc} normalizes the same as {seen_normalized[norm]}: {text!r}")
            else:
                seen_normalized[norm] = doc

        if entry["expected_relation"] == "CONTRADICTS":
            if "contradiction_basis" not in entry or "exclusivity_type" not in entry:
                errors.append(
                    f"[missing-exclusivity] {entry['doc_a']}/{entry['doc_b']}: "
                    f"CONTRADICTS pair has no contradiction_basis/exclusivity_type metadata"
                )
            if entry.get("category") == "direct":
                mismatch = check_direct_attribute_value_mismatch(entry)
                if mismatch:
                    errors.append(f"[semantic-type-mismatch] {entry['doc_a']}/{entry['doc_b']}: {mismatch}")

        if entry["expected_relation"] == "REFINES":
            if check_restrictive_refines_scoping(entry["text_b"]):
                errors.append(
                    f"[refines-restrictive-scope] {entry['doc_b']}: specific claim uses a "
                    f"restrictive qualifier that would not entail the general claim: {entry['text_b']!r}"
                )

        if "template_family_id" not in entry:
            errors.append(f"[missing-metadata] {entry['doc_a']}/{entry['doc_b']}: no template_family_id")
        if entry.get("label_provenance") != "CONSTRUCTION_DEFINED":
            errors.append(f"[missing-metadata] {entry['doc_a']}/{entry['doc_b']}: label_provenance is not CONSTRUCTION_DEFINED")

    # Dev/test split integrity: no template family may appear in both.
    family_splits = {}
    for entry in manifest:
        fam = entry.get("template_family_id")
        split = entry.get("split")
        if fam is None or split is None:
            continue
        family_splits.setdefault(fam, set()).add(split)
    leaked = {fam: splits for fam, splits in family_splits.items() if len(splits) > 1}
    if leaked:
        errors.append(f"[split-leakage] template families appearing in both dev and test: {leaked}")

    # RECTIFIED (P1-E, "FINAL REVIEW" round): a SECOND, independent split
    # audit -- entity-disjointness, not just template-family-disjointness.
    # "The split is template-family-disjoint but not entity-disjoint" was
    # the review's exact concern; this check would catch a regression
    # even though (empirically, as of this fix) the corpus already holds
    # the stronger entity-disjoint property by construction accident (the
    # shared NAME_A/NAME_B iterator never repeats a combination, and the
    # two fixed-subject-per-family categories tie their subject 1:1 to a
    # family that is itself never split).
    entity_pool = _load_entity_name_pool()
    entity_splits = {}
    n_entity_unresolved = 0
    for entry in manifest:
        split = entry.get("split")
        if split is None:
            continue
        key = extract_entity_key(entry, entity_pool)
        if key is None:
            n_entity_unresolved += 1
            continue
        entity_splits.setdefault(key, set()).add(split)
    entity_leaked = {k: splits for k, splits in entity_splits.items() if len(splits) > 1}
    if entity_leaked:
        errors.append(f"[entity-split-leakage] entities appearing in both dev and test: {entity_leaked}")
    if n_entity_unresolved:
        print(f"NOTE: entity key could not be resolved for {n_entity_unresolved}/{len(manifest)} "
              f"pairs (excluded from the entity-disjointness check, not counted as a violation).")

    print(f"Validated {len(manifest)} pairs ({len(manifest) * 2} documents) from {manifest_path}")
    if errors:
        print(f"\n{len(errors)} VALIDATION FAILURES:\n")
        for e in errors[:200]:
            print("  " + e)
        if len(errors) > 200:
            print(f"  ... and {len(errors) - 200} more")
        return 1

    cat_counts = Counter(e["category"] for e in manifest)
    fam_counts = Counter(e["template_family_id"] for e in manifest)
    split_counts = Counter(e["split"] for e in manifest)
    print("All checks passed: no bad-negation, dangling-subject, duplicate, "
          "missing-exclusivity, missing-metadata, split-leakage, entity-split-leakage, "
          "direct-attribute-value-mismatch, or refines-restrictive-scope defects found.")
    print(f"Categories: {len(cat_counts)}, template families: {len(fam_counts)}, split: {dict(split_counts)}")
    print(f"\nSplit-integrity stress tests (P1-E, audit round):")
    print(f"  Family-held-out:        PASS ({len(fam_counts)} families, 0 crossing dev/test)")
    print(f"  Entity-held-out:        PASS ({len(entity_splits)} resolved entity keys, "
          f"0 crossing dev/test, {n_entity_unresolved} pairs unresolved)")
    print(f"  Family+entity-held-out: PASS (both hold simultaneously -- see above)")
    return 0


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MANIFEST
    sys.exit(validate(path))
