# SMRITI-Reference Annotation Protocol (v2.0, abridged from the original human-judge guidelines)

**RECTIFIED (external "reality check" review round 3, P0-10 "annotation
protocol is stale relative to the actual annotation"):** bumped from v1.1
to v2.0 and restructured around three explicit, machine-checkable
schemas (relationship labels, direction, resolution status) plus a
required annotation-metadata record, so this document actually describes
the experiment that produced the numbers in the paper rather than an
earlier design that predates EQUIVALENT and the axis-based direction
convention. Nothing about Task 1 (claim extraction) or the calibration
notes in Task 2 changed in substance -- this is a schema-formalization
pass, not a re-annotation.

## Purpose
Evaluate SMRITI's output claims/relationships against reference labels to compute
precision, recall, F1, and calibration metrics.

## Canonical schemas (read this before annotating)

```text
relationship label (relation_type):
    CONTRADICTS
    SUPPORTS
    REFINES
    EQUIVALENT
    NEUTRAL
    UNSURE            -- annotator-side "I can't call this"; maps to
                         ResolutionStatus.ABSTAINED, never scored as a
                         sixth relation type competing with the other
                         five (see resolution status below and
                         docs/relationship_ontology.md)

direction (SUPPORTS / REFINES only):
    A_TO_B            -- claim A is the confirming/entailing/refining one
    B_TO_A            -- claim B is the confirming/entailing/refining one
    SYMMETRIC         -- not applicable; CONTRADICTS, EQUIVALENT, and
                         NEUTRAL are always symmetric and carry no
                         direction field at all

resolution status (system-side, not annotator-side -- included here so
annotators understand what their UNSURE label becomes downstream):
    RESOLVED          -- relation_type is one of the five real relations
    ABSTAINED         -- relation_type is None; UNSURE on the annotator
                         side, or the system declining to commit
```

`direction` here is the same A_TO_B/B_TO_A axis SMRITI's own bidirectional
resolver (`retrieval/classification/resolver.py`) reasons over --
type-independent, so a SUPPORTS-A_TO_B judgment and a REFINES-A_TO_B
judgment share the same axis value and can be compared directly (this is
what `evaluation/annotation/score.py`'s D1-D4 direction metrics do). An
earlier version of this protocol asked for compound labels
(`A_CONFIRMS_B`/`B_CONFIRMS_A` for SUPPORTS, `A_REFINES_B`/`B_REFINES_A`
for REFINES); those remain valid to encounter in `pass1_relationships.json`/
`pass2_relationships.json` from before this schema was formalized, and
`score.py` maps them onto the A_TO_B/B_TO_A axis internally
(`_GOLD_LABEL_TO_AXIS`) -- new annotation rounds should use `A_TO_B`/
`B_TO_A`/`SYMMETRIC` directly.

## Annotation metadata (required for every new annotation round)

**RECTIFIED (P1 "annotation metadata is insufficient"):** every annotation
round from this version forward must be accompanied by a sibling
`<name>.meta.json` file recording:

```json
{
  "protocol_version": "2.0",
  "model_name": "...",
  "model_revision": "...",
  "temperature": null,
  "seed": null,
  "prompt_hash": "...",
  "sample_seed": null,
  "source_run_id": "...",
  "annotation_timestamp": "...",
  "blind_status": true
}
```

Use `null` with a short explanatory comment (in an accompanying `_note`
field) for any value that was genuinely not recorded at annotation time,
rather than omitting the field or guessing a plausible-looking value --
an honestly-`null` field is far more useful to a future reader than a
fabricated one. `evaluation/annotation/pass1_relationships.meta.json`,
`pass2_relationships.meta.json`, and `rc2_rc3_relationships.meta.json`
apply this retroactively to the three existing rounds, with their
genuinely-unrecoverable fields disclosed as such rather than
back-filled.

## Task 1 — Claim Extraction Validity + Reliability (RC1, RC4)
For each claim (a short text span SMRITI extracted from a source document), judge:

1. **valid** (boolean): Is this a structurally sound, meaningful claim — a complete
   clause with an identifiable subject/predicate (optionally object), OR (for non-English
   script such as Kannada) an exact, non-hallucinated text span? Mark **false** if the
   text is pure noise: a bibliographic/metadata line (e.g. "**Source:** X"), a heading
   fragment with no assertion, a truncated fragment that asserts nothing, or garbled text.
2. **quality** (integer 1-5): If valid, how well-formed/informative is the claim as a
   standalone statement? 5 = fully self-contained and precise; 3 = understandable but
   missing some context; 1 = barely parseable. Use `null` if not valid.
3. **reliability** (integer 1-5): Independent of extraction quality, how epistemically
   reliable/credible is the underlying assertion, given only the claim text and its
   context heading (no external fact-checking — judge based on the kind of claim it is):
   - 5 = overwhelming consensus fact (e.g. basic astronomy, well-established CS/robotics
     architecture facts, textbook algorithm descriptions)
   - 4 = strong domain consensus, standard technical documentation content
   - 3 = plausible but context-dependent or moderately uncertain (recipe technique claims,
     tactical sports opinions presented as fact, single-study findings)
   - 2 = weak evidence, essentially one source's opinion/anecdote dressed as fact
   - 1 = highly suspect, internally inconsistent, or a claim that contradicts
     well-established knowledge
4. **is_negated_correct** / **modality_correct** (boolean, optional sanity check): only
   fill in if you notice the system's negation/modality tag looks wrong — otherwise omit.

## Task 2 — Relationship Classification (RC2, RC3)

**RECTIFIED (bidirectional-NLI rewrite, external review item 10):** the
prior protocol said SUPPORTS' "direction doesn't matter." That was wrong
for a directed knowledge graph: SUPPORTS and REFINES both need a
direction (which claim confirms/elaborates the other), and "A and B say
the same thing" is now its own label (EQUIVALENT) rather than an
unlabeled special case of SUPPORTS. For each pair of claims (A, B),
assign exactly one **relation_type**, and for SUPPORTS/REFINES also give
a **direction**:

- **EQUIVALENT**: A and B assert the same proposition in different
  words — each one, read alone, would let you infer the other. This
  means independently verifying entailment in **both** directions (A ⟹ B
  AND B ⟹ A); high textual/topical similarity alone is NOT sufficient —
  two claims can be highly similar (same entity, same topic, overlapping
  vocabulary) while still asserting different things, which is NEUTRAL or
  REFINES, not EQUIVALENT. No direction needed (symmetric).
- **SUPPORTS** (direction: `A_TO_B` if A is the confirming/entailing
  claim, else `B_TO_A`): one claim independently confirms the other at
  roughly the same level of detail/generality — restating, not adding
  new information.
- **REFINES** (direction: `A_TO_B` if A is the entailing, more specific
  claim, else `B_TO_A`): one claim entails the other AND adds
  detail/specificity the other lacks (a numeric value, a named entity, a
  date, a narrower scope). The *entailing, more specific* claim is the
  one whose ID the direction points away from (e.g. `A_TO_B` means A is
  the specific/entailing claim, refining the more general B).
- **CONTRADICTS**: A explicitly negates or directly opposes B — they
  cannot both be true as stated (direct reversal, methodological
  conflict, or factual conflict). Symmetric, no direction needed.
- **NEUTRAL**: Topically related (or even unrelated) but neither
  supports, contradicts, refines, nor is equivalent.
- **UNSURE**: Genuinely too ambiguous to call — will be excluded from scoring.

When SUPPORTS vs. REFINES is genuinely unclear (e.g. the added detail is
minor), prefer SUPPORTS — REFINES should be reserved for a clear,
material addition of specificity, not any wording difference at all.

Important calibration notes:
- Claims from **completely unrelated domains** (e.g. a robotics claim vs. a cricket claim)
  should almost always be **NEUTRAL**, never CONTRADICTS, even if surface wording overlaps.
- **Temporal/statistical claims from different years** (e.g. "IPL 2025 economy rate X" vs.
  "IPL 2026 squad list") are NEUTRAL unless one explicitly refutes the other's content.
- Do NOT default to CONTRADICTS just because two claims express different opinions on a
  loosely shared topic (e.g. two different curry recipes using different techniques) —
  that is NEUTRAL or REFINES, not CONTRADICTS, unless one explicitly states the other's
  method is wrong/inferior (the corpus's deliberately-planted "rogue" documents, e.g.
  "Pressure Cooking Ruins Lamb Rogan Josh" vs. the pressure-cooker recipes, DO explicitly
  make this claim — that pattern is a genuine CONTRADICTS).

## Output format
You will be given a JSON array of items to label. Produce a JSON **object** (not array)
mapping each item's id to your judgment object, e.g. for Task 1:
```json
{"claim_id_1": {"valid": true, "quality": 4, "reliability": 5}, ...}
```
For Task 2:
```json
{"relationship_id_1": {"label": "CONTRADICTS", "note": "optional short reason"}, ...}
{"relationship_id_2": {"label": "SUPPORTS", "direction": "A_TO_B", "note": "..."}, ...}
{"relationship_id_3": {"label": "REFINES", "direction": "B_TO_A", "note": "..."}, ...}
{"relationship_id_4": {"label": "EQUIVALENT", "note": "..."}, ...}
{"relationship_id_5": {"label": "UNSURE", "note": "..."}, ...}
```
`direction` is required for SUPPORTS and REFINES labels only, and must be
`A_TO_B` or `B_TO_A` (see the canonical schema above) — omit it (or use
`null`) for EQUIVALENT/CONTRADICTS/NEUTRAL/UNSURE, which carry no
direction.
Cover EVERY item in the input file — do not skip any. Work through them systematically;
most calls are straightforward and should take a sentence of reasoning at most. Write
your final answer only as the single JSON object described above, to the exact output
path you are given — no other commentary in that file.
