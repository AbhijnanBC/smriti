# SMRITI

**A reproducible, self-certifying pipeline for claim extraction,
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
| 8. Reliability Scoring | Multi-signal fusion into a single, fully-decomposable reliability index per claim |
| 9. Knowledge API | Query planning, projection control, caching |
| 10. Dashboard | Epistemic-state-driven (certain / contested / stale / unsupported) interactive exploration |
| 11. Runtime | Operational governance: health monitoring, capability model, event bus |
| 12. Evaluation | Gate-based architectural certification and publication-readiness assessment |

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

`evaluation/` contains three independent evaluation layers, deliberately
not mixed together:

- **SMRITI-Reference** (`data/raw/gold_vault/`, evaluation code in
  `evaluation/annotation/`): a 53-document adversarial corpus with
  deliberately contradictory documents, its annotation protocol, two
  independent LLM-derived reference-annotation passes, and the scoring code
  used to compute precision/recall/F1 against them. Named "Reference", not
  "Gold" — the labels are LLM-derived, disclosed as such, and are explicitly
  not presented as a human-annotation substitute (see the paper's
  Limitations).
- **SMRITI-Controlled** (`data/raw/controlled_v1/`, evaluation code in
  `evaluation/controlled/`): a small corpus of deliberately objective,
  unambiguous claim pairs (numeric facts, explicit negation, named-entity
  attribution) whose relationship label is a fact about how the corpus was
  constructed, not an opinion — this needs no annotation pass at all.
- **Metamorphic / self-consistency checks** (`src/smriti/evaluation/scientific/metamorphic.py`,
  `explainability_audit.py`): controlled-perturbation and audit-trail
  reconstruction tests that require no external ground truth of any kind.

`paper/` contains the accompanying research paper (ACL-style LaTeX)
describing all of this in full, including an explicit discussion of what a
genuine human validation study would still need to add. See
`paper/smriti_paper.tex` and `evaluation/annotation/protocol.md`.

## Project status

SMRITI's architecture (phase isolation, immutable data models, full
provenance, reproducibility manifests) is production-quality. Its empirical
validation is disclosed and in progress: see the paper's Limitations section
for exactly what is and is not established by the current evaluation.
