# SMRITI-Gold Annotation Protocol (v1.1, abridged from the original human-judge guidelines)

## Purpose
Evaluate SMRITI's output claims/relationships against reference labels to compute
precision, recall, F1, and calibration metrics.

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
For each pair of claims (A, B), assign exactly one label:
- **SUPPORTS**: A strengthens, confirms, or provides evidence consistent with B (or vice
  versa — direction doesn't matter for this label).
- **CONTRADICTS**: A explicitly negates or directly opposes B — they cannot both be true
  as stated (direct reversal, methodological conflict, or factual conflict).
- **REFINES**: A narrows, qualifies, elaborates, or adds detail to B (or vice versa)
  without contradicting it.
- **NEUTRAL**: Topically related (or even unrelated) but neither supports nor contradicts
  nor refines.
- **UNSURE**: Genuinely too ambiguous to call — will be excluded from scoring.

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
```
Cover EVERY item in the input file — do not skip any. Work through them systematically;
most calls are straightforward and should take a sentence of reasoning at most. Write
your final answer only as the single JSON object described above, to the exact output
path you are given — no other commentary in that file.
