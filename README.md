# SMRITI

**A reproducible, auditable pipeline for claim extraction,
contradiction-aware knowledge graph construction, and reliability scoring
over personal note vaults.**

SMRITI turns a folder of Markdown/PDF notes into a knowledge graph where
every extracted claim carries a fully-explainable reliability score, and
claims that contradict each other are structurally kept apart rather than
silently merged. It is built as twelve phase-isolated stages, each of which
consumes only the immutable output of the previous phase and writes a
manifest recording exactly how its output was produced.

| Phase | Responsibility |
|-------|----------------|
| 1. Discovery | Content-hash based deduplication and incremental file discovery |
| 2. Text Extraction | Multi-format parsing (Markdown, PDF) and normalization |
| 3. Semantic Sentences | Context-aware segmentation, preserving heading hierarchy |
| 4. Claim Construction | Dependency-parse SVO extraction, negation/modality/conditional annotation |
| 5. Embedding | Cached Sentence-BERT embeddings with quality tracking |
| 6. Relationship Discovery | Cosine-similarity candidate retrieval + NLI-based relationship classification |
| 7. Knowledge Graph | Constraint-based signed-graph partitioning that guarantees no two contradicting claims ever share a partition |
| 8. Reliability Scoring | Multi-signal fusion into two fully-decomposable, independently-explainable scores per claim — a `reliability_index` (evidence signals only) and a separate `importance_index` (graph-centrality signals only), never blended into one number |
| 9. Knowledge API | Query planning, projection control, caching |
| 10. Dashboard | Epistemic-state-driven (certain / contested / stale / unsupported) interactive exploration |
| 11. Runtime | Operational governance: health monitoring, capability model, event bus |
| 12. Evaluation | Gate-based architectural certification and artifact-readiness assessment |

## Getting started

```bash
poetry install
poetry run python -m smriti.main pipeline --start 1 --stop 12
poetry run python -m smriti.main ui   # launches the Streamlit dashboard
```

Input notes go under `data/raw/<vault_name>/`. To run the pipeline against a
specific vault in isolation (rather than everything under `data/raw/`), use:

```bash
poetry run python scripts/run_vault.py <vault_name> --start 1 --stop 12
```

## Evaluation and the research paper

`evaluation/` contains several independent evaluation layers, deliberately
not mixed together. The three internally-constructed ones:

- **SMRITI-Reference** (`data/raw/reference_vault/`, evaluation code in
  `evaluation/annotation/`): a 53-document adversarial corpus with
  deliberately contradictory documents, its annotation protocol, two
  independent LLM-derived reference-annotation passes, and the scoring code
  used to compute precision/recall/F1 against them. Named "Reference", not
  "Gold" — the labels are LLM-derived, disclosed as such, and are explicitly
  not presented as a human-annotation substitute (see the paper's
  Limitations).
- **SMRITI-Controlled** (`data/raw/controlled_v1/` for the 32-pair
  hand-written pilot, `data/raw/controlled_v2/` for the sanitized,
  713-pair, 15-category scale-up; evaluation code in
  `evaluation/controlled/` and `evaluation/controlled/v2/`): claim pairs
  whose relationship label is a fact about how the pair was constructed
  (numeric facts, explicit negation with an explicit exclusivity premise,
  named-entity attribution, entailment, equivalence, hard-neutral
  distractors, and deliberately-ambiguous abstention checks), not a human
  or LLM judgment — labeled `label_provenance: CONSTRUCTION_DEFINED`
  throughout, in a file literally named `construction_manifest.json`
  (renamed from `gold_manifest.json`, since "gold" implies a human-
  annotation standard this is not). v2 scales the pilot roughly 22$\times$
  via parameterized templates, split by template family *and* verified
  entity-disjoint into a frozen TEST set and a DEV set never used to
  compute reported numbers, and is checked by
  `evaluation/controlled/generators/validate_corpus.py` (grammar,
  duplicate-text, non-exclusive-contradiction, and split-leakage checks)
  before any number is computed from it. `evaluation/closed_world/v1/`
  builds a second, disjoint 900-pair benchmark from the same
  construction discipline, adding pairs with no known label at all
  outside its own designated set so a reader can see exactly how much
  of the candidate universe remains unlabeled rather than only the
  labeled slice. `evaluation/claim_validity/v1/` independently checks
  Phase 4's claim/non-claim gate against 500 construction-defined spans
  drawn from a large, diverse template pool (not a human or LLM
  judgment either). See `paper/sections/controlled_corpus.tex` and
  `paper/sections/closed_world.tex` for the full category breakdowns and
  disclosed generation methodology.
- **Metamorphic / self-consistency checks** (`src/smriti/evaluation/scientific/metamorphic.py`,
  `explainability_audit.py`): controlled-perturbation and audit-trail
  reconstruction tests that require no external ground truth of any kind.

Two further layers use data SMRITI was never trained or tuned on:

- **External transfer evaluations** (`evaluation/fever/`, `evaluation/scifact/`,
  `evaluation/scifact_open/`): SMRITI's unmodified resolver and NLI model
  scored zero-shot against frozen samples of the public FEVER and SciFact
  benchmarks, with SMRITI's five-way-plus-ABSTAINED label space collapsed
  onto each benchmark's own three-way scheme. Reported as zero-shot
  transfer accuracy, not as an official benchmark-test score.
- **Calibration and selective prediction** (`evaluation/calibration/v1/`):
  a genuine DEV-fit/TEST-frozen temperature-scaling calibrator (ECE,
  Brier, NLL), plus both a classification-only and an end-to-end
  risk-coverage curve — the latter treating a retrieval miss or an
  explicit abstention as a permanent non-commit, not silently excluded
  from the denominator.

Every evaluation category's exact run ID, dataset content hash, model
revision, and dependency-lock hash is tied together in one place:
`evaluation/release_manifest_v1.json` (regenerate with
`scripts/generate_release_manifest.py` after any code or data change).

`paper/` contains the accompanying research paper (ACL-style LaTeX)
describing all of this in full, including an explicit discussion of what a
genuine human validation study would still need to add. See
`paper/smriti_paper.tex` and `evaluation/annotation/protocol.md`.

## Project status

SMRITI's architecture has been extensively tested (phase isolation, immutable
data models, full provenance, reproducibility manifests); empirical
validation is disclosed and ongoing, not claimed as complete. See the paper's
Limitations section for exactly what is and is not established by the
current evaluation, and its Discovered Defects section for a full account of
what external review has found and this project has fixed so far.
