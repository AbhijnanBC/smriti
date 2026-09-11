"""
build_benchmark.py -- SMRITI-ClaimValidity-v1: a construction-defined
claim-extraction semantic benchmark (P1-7, "PLEASE FIX AND SAVE ME"
review round).

The problem this closes: Phase 4's own validator explicitly does not
evaluate claim SEMANTICS -- it can prove "I don't emit headings,
metadata, code, etc." but not "the objects I do emit are genuinely
valid declarative claims." This benchmark gives AssertionClassifier
(claims/classifier.py, the rule-based Phase 4 gate that decides this
before any Claim is built) a set of candidate spans with a
CONSTRUCTION-DEFINED ground truth -- DECLARATIVE_CLAIM, NON_CLAIM, or
AMBIGUOUS -- independent of whatever the classifier itself would decide,
so scoring it against this benchmark is not circular.

RECTIFIED (P1-F, "FINAL REVIEW" round): the previous version drew each
NON_CLAIM subtype and every AMBIGUOUS span from a small (~10-20 item)
fixed template pool sampled with modulo indexing, so most of a
category's 20-45 instances were VERBATIM duplicates of one of a handful
of strings -- e.g. all 22 "heading" instances were one of only 10
distinct headings, each repeated ~2.2 times. A classifier (or a future
learned one) could pass this benchmark by memorizing template wording
rather than the semantic function (heading vs. claim vs. question) the
category is supposed to test. Every category below now:
  (a) draws from a substantially larger template pool,
  (b) crosses templates with entity substitution wherever the template
      allows it (multiple entities x multiple templates, not just
      multiple templates), and mixes in entity-free generic phrasings
      too (multiple lexical realizations, not just entity swaps),
  (c) varies length and syntactic form within a category (short
      fragments alongside longer subordinate-clause sentences), and
  (d) records which literal template produced each entry
      (`template_id`) plus a template-level `split` (`train`/
      `template_heldout`), stratified per category exactly like
      build_controlled_v2.py's family split, so a template-held-out
      evaluation is possible (see run_claim_validity_eval.py) -- a
      literal template string never appears in both splits.
The benchmark reports unique_text_count / template_count /
instances_per_template per category so the diversity improvement itself
is checkable, not just asserted.

No human annotation (unavailable for this project, per the review's own
allowance: "A carefully designed independently generated/reference
benchmark is acceptable for now"). 500 spans: 200 unambiguous
DECLARATIVE_CLAIM, 200 unambiguous NON_CLAIM (spread across the 9
non-assertion AssertionType subtypes the classifier can emit), and 100
genuinely AMBIGUOUS spans (bare gerund phrases, elliptical clauses,
nominalized headers that could read either way) -- these are NOT scored
right/wrong (there is no single correct answer for a genuinely
ambiguous span by design), only reported as a resolution distribution,
exactly the same "selective prediction," not "accuracy against a label
that doesn't exist," framing this paper already applies to
SMRITI-Controlled-v2's ambiguous_abstention category (see \\S{sec:controlled}
in the paper).

Run with: poetry run python evaluation/claim_validity/v1/build_benchmark.py
"""
import itertools
import json
import random
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT_PATH = ROOT / "evaluation" / "claim_validity" / "v1" / "benchmark.json"

random.seed(20260911)

ENTITIES = [
    "The Meridian cluster", "The Oakmere scheduler", "The Falcon pipeline",
    "The Titan registry", "The Vantage gateway", "The Kelvor daemon",
    "The Draymoor index", "The Brackwood cache", "The Larkspur queue",
    "The Norwich fabric", "The Farrow relay", "The Renfield kernel",
    "The Osprey ledger", "The Talbrook substrate", "The Windmere module",
    "The Colby array", "The Dunmore server", "The Ivestone router",
    "The Cassian codec", "The Marlow grid", "The Halloway sensor",
    "The Aerotrix scheduler", "The Solvex pipeline", "The Quorren cache",
    "The Vesper daemon",
]

# entity-free variant used by templates whose "{e}" slot is optional --
# a template appears both with and without an entity substitution so the
# benchmark also contains lexical realizations that do not depend on the
# fictional-entity vocabulary at all.
GENERIC_SUBJECTS = [
    "This component", "The affected service", "The subsystem in question",
    "The upstream dependency", "The current implementation",
]

# ── DECLARATIVE_CLAIM: varied structurally-complete assertions.
#    RECTIFIED (P1-F): pool widened from 10 to 22 templates spanning
#    passive voice, subordinate/conditional clauses, short vs. long
#    forms, and reported-claim framing (multiple syntactic forms) -----
DC_TEMPLATES = [
    "{e} processes requests in under ten milliseconds.",
    "{e} was deprecated in the third quarter of last year.",
    "{e} does not support concurrent writes.",
    "{e} and its successor share the same configuration format.",
    "{e} is faster than the previous implementation.",
    "Independent benchmarks confirm that {e} reduces average latency.",
    "{e} requires at least four gigabytes of memory to start.",
    "If load exceeds capacity, {e} rejects new connections.",
    "{e} was rewritten to eliminate a memory leak.",
    "The team responsible for {e} reported a critical vulnerability.",
    "{e} is maintained by a rotating on-call team.",
    "Once initialized, {e} cannot change its storage backend.",
    "{e} was retired after the migration completed.",
    "{e} handles roughly twice the traffic it did a year ago.",
    "Because it lacks a retry policy, {e} drops requests during failover.",
    "{e} runs as a single replica in every region except the primary one.",
    "A configuration error in {e} caused the outage on record.",
    "{e} no longer depends on the legacy authentication service.",
    "{e} was designed before the current scaling requirements existed.",
    "Every deployment of {e} is provisioned from the same base image.",
    "{e} silently discards malformed input instead of raising an error.",
    "{e} has never failed a scheduled integrity check.",
]

# ── NON_CLAIM subtypes. RECTIFIED (P1-F): every pool below is at least
#    2x its previous size, crossed with entities/generic subjects where
#    the template has an "{e}" slot, so instances/template drops sharply
#    and repeated instances of the SAME literal template are no longer
#    the norm within a category. -------------------------------------
HEADING_TEMPLATES = [
    "Overview", "Configuration", "Getting Started", "Known Limitations",
    "System Requirements", "Deployment Notes", "Troubleshooting Guide",
    "Release Notes", "API Reference", "Performance Tuning",
    "{e} Overview", "{e} Configuration Guide", "Getting Started with {e}",
    "{e} Known Limitations", "{e} System Requirements",
    "{e} Deployment Notes", "{e} Troubleshooting Guide",
    "{e} Release Notes", "{e} API Reference", "{e} Performance Tuning",
    "Appendix", "Glossary", "Change Log", "Index", "Prerequisites",
    "Frequently Asked Questions",
]
METADATA_TEMPLATES = [
    "**Source:** Internal Engineering Wiki", "**Contradicts:** Section 4.2",
    "**Author:** Infrastructure Team", "**Version:** 2.3.1",
    "**Status:** Deprecated", "**Owner:** Platform Group",
    "**Reviewed by:** Release Engineering", "**Last updated:** last quarter",
    "**License:** Internal Use Only", "**Category:** Reliability",
    "**Component:** {e}", "**Applies to:** {e}", "**Maintainer:** {e} team",
    "**Tags:** infrastructure, internal", "**Priority:** P2",
    "**Environment:** production", "**Region:** multi-region",
    "**Approved by:** Change Advisory Board", "**Ticket:** INFRA-4821",
    "**Revision:** draft",
]
QUESTION_TEMPLATES = [
    "What is the maximum request size?", "How often does the cache refresh?",
    "Why does the scheduler reject this job?", "Which region hosts the primary replica?",
    "Can this configuration be overridden?", "When was this feature introduced?",
    "Who maintains this component?", "Does this affect the free tier?",
    "What happens during a failover?", "Is this behavior configurable?",
    "What is the maximum request size for {e}?",
    "How often does {e} refresh its cache?",
    "Why does {e} reject this kind of job?",
    "Which region hosts {e}'s primary replica?",
    "Can {e}'s configuration be overridden?",
    "When was this feature added to {e}?",
    "Who is currently responsible for {e}?",
    "Does this change affect {e} in the free tier?",
    "What happens to {e} during a failover?",
    "Is {e}'s retry behavior configurable?",
]
PROCEDURAL_TEMPLATES = [
    "Restart the service after editing the configuration file.",
    "Set the environment variable before running the script.",
    "Back up the database before applying the migration.",
    "Increase the timeout if requests are failing.",
    "Check the logs for errors before escalating.",
    "Install the dependency listed in the manifest.",
    "Verify the checksum after downloading the archive.",
    "Disable the feature flag if issues persist.",
    "Rotate the credentials every ninety days.",
    "Clear the cache before re-running the benchmark.",
    "Restart {e} after editing its configuration file.",
    "Set the environment variable before starting {e}.",
    "Back up {e}'s data store before applying the migration.",
    "Increase {e}'s timeout if requests keep failing.",
    "Check {e}'s logs for errors before escalating.",
    "Disable {e}'s feature flag if issues persist.",
    "Rotate {e}'s credentials every ninety days.",
    "Clear {e}'s cache before re-running the benchmark.",
]
LIST_ITEM_TEMPLATES = [
    "Two gigabytes of RAM", "A valid API key", "Network access on port 443",
    "The latest client library", "A configured storage backend",
    "Read access to the shared bucket", "An active support contract",
    "The updated schema file", "A backup of the previous state",
    "Administrator privileges", "A valid API key for {e}",
    "Read access to {e}'s shared bucket", "The latest client library for {e}",
    "A configured storage backend for {e}", "An active support contract for {e}",
    "Administrator privileges on {e}", "A recent backup of {e}'s state",
    "The updated schema file for {e}",
]
TABLE_CELL_TEMPLATES = [
    "99.9% uptime", "v2.3.1", "us-east-1", "512 MB", "Enabled",
    "2024-07-01", "Critical", "3 replicas", "TLS 1.3", "Deprecated",
    "99.95% uptime", "v3.0.0-rc1", "eu-west-2", "1 GB", "Disabled",
    "2025-01-15", "Low", "5 replicas", "TLS 1.2", "Active",
    "N/A", "Pending", "8 vCPUs", "ap-southeast-1", "Read-only",
]
CODE_TEMPLATES = [
    "config.set('timeout', 30)", "SELECT * FROM claims WHERE id = ?",
    "if retries > max_retries: raise Error", "docker run -p 8080:8080 app",
    "export PATH=$PATH:/usr/local/bin", "return response.json()",
    "assert result.status == 200", "for claim in claims: process(claim)",
    "git checkout -b feature/new-signal", "npm install --save-dev",
    "kubectl rollout restart deployment/api", "curl -s http://localhost/health",
    "cache.invalidate(key)", "logger.warning('retrying request')",
    "SELECT count(*) FROM events WHERE status = 'failed'",
    "self.assertEqual(actual, expected)", "poetry run pytest -q",
    "with open(path) as f: data = json.load(f)",
]
QUOTE_TEMPLATES = [
    "This is exactly the kind of failure we designed the gate to catch.",
    "We should not ship this without a rollback plan.",
    "The original design assumed single-tenant deployment.",
    "Nobody on the team anticipated this edge case.",
    "This is a known tradeoff, not an oversight.",
    "The migration path was never actually tested end to end.",
    "We deprioritized this in favor of the retrieval fix.",
    "This matches the behavior described in the original RFC.",
    "The regression only appears under sustained load.",
    "This was flagged in review but never actioned.",
    "It worked in staging, which is exactly what worries me.",
    "We are trading correctness for availability here, deliberately.",
    "The postmortem never actually named a root cause.",
    "This is the third time this exact alert has fired this month.",
    "Nobody owns this anymore, which is the real problem.",
]
FRAGMENT_TEMPLATES = [
    "of the the cluster when", "into via without the",
    "because also therefore not", "-- see above for --",
    "under over across through", "the a an of to",
    "and but or nor yet", "with without within through",
    "-> -> -> null", "TODO TODO TODO fix this",
    "pending pending pending", "see section see section",
    "et al. et al.", "[citation needed] [citation needed]",
]


def make_entry(idx_prefix, i, text, gold_label, template_id, origin_block_type="paragraph", category=None):
    return {
        "id": f"{idx_prefix}{i:03d}",
        "text": text,
        "origin_block_type": origin_block_type,
        "gold_label": gold_label,
        "category": category or gold_label,
        "template_id": template_id,
        "split": None,  # assigned in a stratified template-level pass below
    }


def _instantiate(templates, category_prefix):
    """
    Cross every template that has an "{e}" slot with ENTITIES/
    GENERIC_SUBJECTS; templates without a slot are used as-is. Returns
    a list of (template_id, rendered_text) pairs, deduplicated so the
    same literal template never yields the exact same rendered text
    twice by accident of substitution overlap.
    """
    out = []
    for ti, template in enumerate(templates):
        tid = f"{category_prefix}-{ti:02d}"
        if "{e}" in template:
            subjects = ENTITIES + GENERIC_SUBJECTS
            for subject in subjects:
                out.append((tid, template.format(e=subject)))
        else:
            out.append((tid, template))
    return out


def _assign_template_splits(entries, heldout_fraction=0.2):
    """
    RECTIFIED (P1-F, "FINAL REVIEW" round): template-held-out split,
    stratified per category exactly like build_controlled_v2.py's
    family split (never split one category's only template, and never
    globally hash so a whole category could land with zero heldout
    templates by chance). A literal template_id is entirely in `train`
    or entirely in `template_heldout`, never both.
    """
    templates_by_cat = {}
    for e in entries:
        templates_by_cat.setdefault(e["category"], set()).add(e["template_id"])
    template_to_split = {}
    for cat, templates in templates_by_cat.items():
        templates = sorted(templates)
        rng = random.Random(f"{cat}-split-20260911")
        rng.shuffle(templates)
        n_heldout = max(1, round(len(templates) * heldout_fraction)) if len(templates) > 1 else 0
        for i, tid in enumerate(templates):
            template_to_split[tid] = "template_heldout" if i < n_heldout else "train"
    for e in entries:
        e["split"] = template_to_split[e["template_id"]]


def main():
    entries = []

    # 200 DECLARATIVE_CLAIM, drawn from all (template x entity) combinations.
    dc_pairs = _instantiate(DC_TEMPLATES, "DC")
    random.shuffle(dc_pairs)
    dc_pairs = dc_pairs[:200]
    for i, (tid, text) in enumerate(dc_pairs):
        entries.append(make_entry("DC", i, text, "DECLARATIVE_CLAIM", tid))

    # 200 NON_CLAIM, spread across 9 subtypes (~22 each, last group gets remainder).
    non_claim_groups = [
        ("heading", HEADING_TEMPLATES, "paragraph"),
        ("metadata", METADATA_TEMPLATES, "paragraph"),
        ("question", QUESTION_TEMPLATES, "paragraph"),
        ("procedural_instruction", PROCEDURAL_TEMPLATES, "paragraph"),
        ("list_item", LIST_ITEM_TEMPLATES, "bullet_item"),
        ("table_cell", TABLE_CELL_TEMPLATES, "table"),
        ("code", CODE_TEMPLATES, "code_block"),
        ("quote", QUOTE_TEMPLATES, "block_quote"),
        ("fragment", FRAGMENT_TEMPLATES, "paragraph"),
    ]
    per_group = 200 // len(non_claim_groups)
    remainder = 200 - per_group * len(non_claim_groups)
    nc_i = 0
    for gi, (cat, templates, origin) in enumerate(non_claim_groups):
        count = per_group + (1 if gi < remainder else 0)
        pairs = _instantiate(templates, cat)
        rng = random.Random(f"{cat}-instantiate-20260911")
        rng.shuffle(pairs)
        # Sample with replacement only if the crossed pool is smaller than
        # the target count (true for table_cell/code/quote/fragment, which
        # have no "{e}" slot); otherwise sample without replacement.
        if len(pairs) >= count:
            chosen = pairs[:count]
        else:
            chosen = [pairs[i % len(pairs)] for i in range(count)]
        for tid, text in chosen:
            entries.append(make_entry("NC", nc_i, text, "NON_CLAIM", tid, origin_block_type=origin, category=cat))
            nc_i += 1

    # 100 AMBIGUOUS: bare gerund phrases (entity-substituted where natural)
    # and elliptical/nominalized fragments (generic, no entity slot).
    ambiguous_gerund_templates = [
        "Preparing the Dough", "Handling Retries Gracefully", "Scaling Under Load",
        "Migrating Legacy Configurations", "Balancing Consistency and Availability",
        "Detecting Silent Failures", "Reducing Cold-Start Latency",
        "Coordinating Distributed Writes", "Recovering from Partial Outages",
        "Auditing Access Patterns",
        "Migrating {e}'s Legacy Configuration", "Reducing {e}'s Cold-Start Latency",
        "Coordinating {e}'s Distributed Writes", "Recovering {e} from Partial Outages",
        "Auditing {e}'s Access Patterns", "Scaling {e} Under Load",
        "Detecting Silent Failures in {e}",
    ]
    ambiguous_modal_templates = [
        "Still under investigation", "Pending further review",
        "Subject to change without notice", "Not yet fully validated",
        "Consistent with prior observations", "Likely but not confirmed",
        "A known but unresolved tradeoff", "Partially addressed in this release",
        "Expected in the next iteration", "Under active discussion",
        "Deferred to a future release", "Considered low risk for now",
        "Not applicable in this configuration", "Awaiting sign-off",
        "Believed to be resolved, unverified", "Marked as tentative",
        "Open to reinterpretation",
    ]
    am_gerund_pairs = _instantiate(ambiguous_gerund_templates, "AM-G")
    am_modal_pairs = [(f"AM-M-{i:02d}", t) for i, t in enumerate(ambiguous_modal_templates)]
    am_pool = am_gerund_pairs + am_modal_pairs
    rng = random.Random("ambiguous-instantiate-20260911")
    rng.shuffle(am_pool)
    am_chosen = [am_pool[i % len(am_pool)] for i in range(100)]
    for i, (tid, text) in enumerate(am_chosen):
        entries.append(make_entry("AM", i, text, "AMBIGUOUS", tid))

    assert len(entries) == 500, len(entries)

    _assign_template_splits(entries)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(entries)} spans to {OUT_PATH}")
    print("Gold label counts:", Counter(e["gold_label"] for e in entries))
    print("NON_CLAIM category counts:",
          Counter(e["category"] for e in entries if e["gold_label"] == "NON_CLAIM"))

    # RECTIFIED (P1-F): report the diversity metrics the review asked
    # for, per category, so the improvement is checkable, not asserted.
    print("\nDiversity (P1-F, audit round):")
    by_cat = {}
    for e in entries:
        by_cat.setdefault(e["category"], []).append(e)
    for cat, es in sorted(by_cat.items()):
        unique_texts = len({e["text"] for e in es})
        templates_used = len({e["template_id"] for e in es})
        splits = Counter(e["split"] for e in es)
        print(f"  {cat:<22} n={len(es):>3}  unique_text_count={unique_texts:>3}  "
              f"template_count={templates_used:>3}  "
              f"instances_per_template={len(es)/templates_used:.2f}  "
              f"split={dict(splits)}")


if __name__ == "__main__":
    main()
