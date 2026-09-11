"""
run_semantic_invariant_audit.py -- post-fix invariant audit (external
"reality check" review round 3, follow-up request).

A single, compact pass/fail check that the P0-1..P0-6 fixes actually hold
as invariants, not just that the specific bugs found are gone. Three
groups, each printed as a checklist:

  CORPUS      -- controlled-v2 corpus-construction invariants (delegates
                 to validate_corpus.py's checks plus two extra ones it
                 doesn't cover: manifest<->file bijection, unsupported
                 relation labels).
  RESOLVER    -- the six-way decision-tree invariant, exercised directly
                 against RelationshipResolver with synthetic NLI score
                 combinations covering every branch.
  CONFIDENCE  -- calibrated_confidence_b_to_a is populated, symmetric
                 relations get SYMMETRIC direction, compute_decision_confidence
                 selects/combines the correct reading per relation type,
                 and the validator's contradictory-evidence check reads
                 both directions.

Run with: poetry run python scripts/run_semantic_invariant_audit.py
Exits non-zero if any check fails.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from smriti.core.models import (
    RelationshipEvidence, NLIScores, InferenceMetadata, CandidatePair,
    RelationshipType, RelationshipDirection, LifecycleStage, ResolutionStatus,
)
from smriti.retrieval.classification.resolver import (
    RelationshipResolver, ResolverPolicy, compute_decision_confidence,
)
from smriti.retrieval.classification.validator import validate_relationship

RESULTS = []


def check(group, name, passed, detail=""):
    RESULTS.append((group, name, passed, detail))
    icon = "PASS" if passed else "FAIL"
    print(f"  [{icon}] {name}" + (f" -- {detail}" if detail and not passed else ""))


def nli(entailment, neutral, contradiction):
    scores = {"entailment": entailment, "neutral": neutral, "contradiction": contradiction}
    return NLIScores(
        entailment_score=entailment, neutral_score=neutral, contradiction_score=contradiction,
        predicted_label=max(scores, key=scores.get), raw_confidence=max(entailment, neutral, contradiction),
    )


def make_evidence(ab, ba, cos=0.9, cal_ab=None, cal_ba=None):
    ab_scores = nli(*ab)
    ba_scores = nli(*ba) if ba is not None else None
    pair = CandidatePair(claim_id_a="A", claim_id_b="B", cosine_similarity=cos, candidate_rank=1)
    return RelationshipEvidence(
        pair=pair, cosine_similarity=cos, nli_scores=ab_scores, nli_scores_b_to_a=ba_scores,
        calibrated_confidence=cal_ab if cal_ab is not None else ab_scores.raw_confidence,
        calibrated_confidence_b_to_a=(cal_ba if cal_ba is not None else (ba_scores.raw_confidence if ba_scores else None)),
        inference_metadata=InferenceMetadata(model_name="test"),
        lifecycle_stage=LifecycleStage.CALIBRATED_EVIDENCE,
    )


def audit_corpus():
    print("\nCORPUS (SMRITI-Controlled-v2)")
    sys.path.insert(0, str(ROOT / "evaluation" / "controlled" / "generators"))
    import validate_corpus as vc

    manifest_path = ROOT / "evaluation" / "controlled" / "v2" / "construction_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rc = vc.validate(manifest_path)
    check("CORPUS", "validate_corpus.py full sweep (grammar/duplicates/exclusivity/"
                     "split-leakage/attribute-value-domain/refines-scoping)", rc == 0)

    corpus_dir = ROOT / "data" / "raw" / "controlled_v2"
    expected_files = set()
    for e in manifest:
        expected_files.add(e["doc_a"] + ".md")
        expected_files.add(e["doc_b"] + ".md")
    actual_files = {p.name for p in corpus_dir.glob("*.md")}
    missing = expected_files - actual_files
    orphaned = actual_files - expected_files
    check("CORPUS", "manifest<->file bijection (every manifest doc has a file, "
                     "no orphan files)", not missing and not orphaned,
          f"missing={list(missing)[:5]} orphaned={list(orphaned)[:5]}")

    known_labels = {"CONTRADICTS", "SUPPORTS", "REFINES", "EQUIVALENT", "NEUTRAL"}
    known_statuses = {"RESOLVED", "ABSTAINED"}
    bad_labels = {e["expected_relation"] for e in manifest if e["expected_relation"] is not None} - known_labels
    check("CORPUS", "0 unsupported relation labels in manifest", not bad_labels, str(bad_labels))
    bad_statuses = {e["expected_status"] for e in manifest} - known_statuses
    check("CORPUS", "0 unsupported expected_status values in manifest", not bad_statuses, str(bad_statuses))
    inconsistent = [
        e for e in manifest
        if (e["expected_status"] == "ABSTAINED") != (e["expected_relation"] is None)
    ]
    check("CORPUS", "expected_relation is null iff expected_status is ABSTAINED",
          not inconsistent, f"{len(inconsistent)} entries violate this")


def audit_closed_world():
    print("\nCLOSED-WORLD BENCHMARK (SMRITI-ClosedWorld-v1, P0-8)")
    manifest_path = ROOT / "evaluation" / "closed_world" / "v1" / "construction_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    check("CLOSED-WORLD", "manifest has exactly 900 pairs", len(manifest) == 900, str(len(manifest)))

    known_buckets = {"intended", "guaranteed_neutral_distractor", "guaranteed_contradiction_distractor"}
    bad_buckets = {e["bucket"] for e in manifest} - known_buckets
    check("CLOSED-WORLD", "0 unrecognized buckets in manifest", not bad_buckets, str(bad_buckets))

    from collections import Counter
    bucket_counts = Counter(e["bucket"] for e in manifest)
    check("CLOSED-WORLD", "each bucket has exactly 300 pairs",
          all(bucket_counts[b] == 300 for b in known_buckets), str(dict(bucket_counts)))

    neutral_wrong_label = [
        e for e in manifest
        if e["bucket"] == "guaranteed_neutral_distractor" and e["expected_relation"] != "NEUTRAL"
    ]
    check("CLOSED-WORLD", "every guaranteed_neutral_distractor pair is labeled NEUTRAL",
          not neutral_wrong_label, f"{len(neutral_wrong_label)} mislabeled")

    contra_wrong_label = [
        e for e in manifest
        if e["bucket"] == "guaranteed_contradiction_distractor" and e["expected_relation"] != "CONTRADICTS"
    ]
    check("CLOSED-WORLD", "every guaranteed_contradiction_distractor pair is labeled CONTRADICTS",
          not contra_wrong_label, f"{len(contra_wrong_label)} mislabeled")

    corpus_dir = ROOT / "data" / "raw" / "closed_world_v1"
    expected_files = set()
    for e in manifest:
        expected_files.add(e["doc_a"] + ".md")
        expected_files.add(e["doc_b"] + ".md")
    actual_files = {p.name for p in corpus_dir.glob("*.md")}
    missing = expected_files - actual_files
    orphaned = actual_files - expected_files
    check("CLOSED-WORLD", "manifest<->file bijection (900 pairs, 1800 documents)",
          not missing and not orphaned, f"missing={list(missing)[:5]} orphaned={list(orphaned)[:5]}")

    all_texts = [e["text_a"] for e in manifest] + [e["text_b"] for e in manifest]
    check("CLOSED-WORLD", "no duplicate claim text within the benchmark",
          len(all_texts) == len(set(all_texts)), f"{len(all_texts) - len(set(all_texts))} duplicates")


def audit_fever():
    print("\nFEVER TRANSFER BENCHMARK (P0-9)")
    sample_path = ROOT / "evaluation" / "fever" / "v1" / "sample.json"
    sample = json.loads(sample_path.read_text(encoding="utf-8"))
    check("FEVER", "sample has exactly 900 pairs", len(sample) == 900, str(len(sample)))

    from collections import Counter
    label_counts = Counter(e["gold_label"] for e in sample)
    known_labels = {"SUPPORTS", "REFUTES", "NOT ENOUGH INFO"}
    check("FEVER", "0 unrecognized gold labels in sample",
          not (set(label_counts) - known_labels), str(dict(label_counts)))
    check("FEVER", "exactly 300 pairs per label",
          all(label_counts[l] == 300 for l in known_labels), str(dict(label_counts)))

    ids = [e["fever_id"] for e in sample]
    check("FEVER", "no duplicate fever_id in sample", len(ids) == len(set(ids)),
          f"{len(ids) - len(set(ids))} duplicates")

    results_path = ROOT / "evaluation" / "fever" / "v1" / "results.json"
    if results_path.exists():
        results = json.loads(results_path.read_text(encoding="utf-8"))
        check("FEVER", "results.json scored all 900 sample pairs",
              results["n_pairs"] == 900, str(results["n_pairs"]))
        rows = results["rows"]
        bad_labels = {r["predicted_fever_label"] for r in rows} - known_labels
        check("FEVER", "0 unrecognized predicted labels in results",
              not bad_labels, str(bad_labels))
        status_relation_consistent = all(
            (r["smriti_status"] == "abstained") == (r["smriti_relation_type"] is None)
            for r in rows
        )
        check("FEVER", "smriti_relation_type is null iff smriti_status is abstained",
              status_relation_consistent, "violation found" if not status_relation_consistent else "")
    else:
        check("FEVER", "results.json exists (skipped detail checks)", False,
              "run evaluation/fever/v1/run_fever_eval.py")


def audit_scifact():
    print("\nSCIFACT TRANSFER BENCHMARK (P0-9)")
    sample_path = ROOT / "evaluation" / "scifact" / "v1" / "sample.json"
    sample = json.loads(sample_path.read_text(encoding="utf-8"))
    check("SCIFACT", "sample has exactly 795 pairs", len(sample) == 795, str(len(sample)))

    from collections import Counter
    label_counts = Counter(e["gold_label"] for e in sample)
    known_labels = {"SUPPORT", "CONTRADICT", "NEI"}
    check("SCIFACT", "0 unrecognized gold labels in sample",
          not (set(label_counts) - known_labels), str(dict(label_counts)))
    check("SCIFACT", "exactly 265 pairs per label",
          all(label_counts[l] == 265 for l in known_labels), str(dict(label_counts)))

    results_path = ROOT / "evaluation" / "scifact" / "v1" / "results.json"
    if results_path.exists():
        results = json.loads(results_path.read_text(encoding="utf-8"))
        check("SCIFACT", "results.json scored all 795 sample pairs",
              results["n_pairs"] == 795, str(results["n_pairs"]))
        rows = results["rows"]
        bad_labels = {r["predicted_scifact_label"] for r in rows} - known_labels
        check("SCIFACT", "0 unrecognized predicted labels in results",
              not bad_labels, str(bad_labels))
        status_relation_consistent = all(
            (r["smriti_status"] == "abstained") == (r["smriti_relation_type"] is None)
            for r in rows
        )
        check("SCIFACT", "smriti_relation_type is null iff smriti_status is abstained",
              status_relation_consistent, "violation found" if not status_relation_consistent else "")
    else:
        check("SCIFACT", "results.json exists (skipped detail checks)", False,
              "run evaluation/scifact/v1/run_scifact_eval.py")


def audit_scifact_open():
    print("\nSCIFACT-OPEN TRANSFER BENCHMARK (P0-9)")
    sample_path = ROOT / "evaluation" / "scifact_open" / "v1" / "sample.json"
    sample = json.loads(sample_path.read_text(encoding="utf-8"))
    check("SCIFACT-OPEN", "sample has exactly 412 pairs", len(sample) == 412, str(len(sample)))

    from collections import Counter
    bucket_counts = Counter(e["bucket"] for e in sample)
    known_buckets = {"genuine_evidence", "unverified_random_distractor"}
    check("SCIFACT-OPEN", "0 unrecognized buckets in sample",
          not (set(bucket_counts) - known_buckets), str(dict(bucket_counts)))
    check("SCIFACT-OPEN", "each bucket has exactly 206 pairs",
          all(bucket_counts[b] == 206 for b in known_buckets), str(dict(bucket_counts)))

    distractor_wrong_label = [
        e for e in sample if e["bucket"] == "unverified_random_distractor" and e["gold_label"] != "NEI"
    ]
    check("SCIFACT-OPEN", "every unverified_random_distractor pair is labeled NEI",
          not distractor_wrong_label, f"{len(distractor_wrong_label)} mislabeled")

    genuine_labels = {e["gold_label"] for e in sample if e["bucket"] == "genuine_evidence"}
    check("SCIFACT-OPEN", "genuine_evidence pairs are only SUPPORT/CONTRADICT",
          genuine_labels <= {"SUPPORT", "CONTRADICT"}, str(genuine_labels))

    results_path = ROOT / "evaluation" / "scifact_open" / "v1" / "results.json"
    if results_path.exists():
        results = json.loads(results_path.read_text(encoding="utf-8"))
        check("SCIFACT-OPEN", "results.json scored all 412 sample pairs",
              results["n_pairs"] == 412, str(results["n_pairs"]))
    else:
        check("SCIFACT-OPEN", "results.json exists (skipped detail checks)", False,
              "run evaluation/scifact_open/v1/run_scifact_open_eval.py")


def audit_calibration():
    print("\nCALIBRATION EXPERIMENT (P1-1)")
    results_path = ROOT / "evaluation" / "calibration" / "v1" / "results.json"
    if not results_path.exists():
        check("CALIBRATION", "results.json exists", False,
              "run evaluation/calibration/v1/fit_calibration.py")
        return
    results = json.loads(results_path.read_text(encoding="utf-8"))
    check("CALIBRATION", "fitted_temperature is positive",
          results["fitted_temperature"] > 0, str(results["fitted_temperature"]))
    check("CALIBRATION", "DEV and TEST pool sizes are non-trivial (>50 each)",
          results["dev_raw_T1"]["n"] > 50 and results["test_raw_T1"]["n"] > 50,
          f"dev={results['dev_raw_T1']['n']} test={results['test_raw_T1']['n']}")
    dev_acc_raw = results["dev_raw_T1"]["accuracy"]
    dev_acc_cal = results["dev_calibrated"]["accuracy"]
    check("CALIBRATION", "calibration never changes accuracy (rescales confidence only)",
          dev_acc_raw == dev_acc_cal, f"{dev_acc_raw} != {dev_acc_cal}")
    test_acc_raw = results["test_raw_T1"]["accuracy"]
    test_acc_cal = results["test_calibrated"]["accuracy"]
    check("CALIBRATION", "calibration never changes TEST accuracy either",
          test_acc_raw == test_acc_cal, f"{test_acc_raw} != {test_acc_cal}")
    check("CALIBRATION", "TEST ECE improves after calibration (frozen T, not fit on TEST)",
          results["test_calibrated"]["ece"] < results["test_raw_T1"]["ece"],
          f"{results['test_calibrated']['ece']} >= {results['test_raw_T1']['ece']}")


def audit_risk_coverage():
    print("\nRISK-COVERAGE CURVE (P1-2)")
    results_path = ROOT / "evaluation" / "calibration" / "v1" / "risk_coverage_results.json"
    if not results_path.exists():
        check("RISK-COVERAGE", "results exist", False,
              "run evaluation/calibration/v1/risk_coverage.py")
        return
    results = json.loads(results_path.read_text(encoding="utf-8"))
    check("RISK-COVERAGE", "TEST AURC in [0, 1]",
          0 <= results["test_aurc"] <= 1, str(results["test_aurc"]))
    check("RISK-COVERAGE", "TEST curve has 20 coverage points",
          len(results["test_curve"]) == 20, str(len(results["test_curve"])))
    check("RISK-COVERAGE", "risk at 100% coverage equals TEST error rate",
          abs(results["test_curve"][-1]["risk"] - results["test_risk_at_full_coverage"]) < 1e-9,
          str(results["test_curve"][-1]["risk"]))
    check("RISK-COVERAGE", "coverage is non-decreasing across the curve",
          all(results["test_curve"][i]["coverage"] <= results["test_curve"][i + 1]["coverage"]
              for i in range(len(results["test_curve"]) - 1)),
          "coverage out of order")
    check("RISK-COVERAGE", "n_kept is non-decreasing across the curve",
          all(results["test_curve"][i]["n_kept"] <= results["test_curve"][i + 1]["n_kept"]
              for i in range(len(results["test_curve"]) - 1)),
          "n_kept out of order")


def audit_direction():
    print("\nEXTERNAL DIRECTION BENCHMARK (P1-3)")
    results_path = ROOT / "evaluation" / "direction" / "v1" / "results.json"
    if not results_path.exists():
        check("DIRECTION", "results exist", False,
              "run evaluation/direction/v1/run_direction_eval.py")
        return
    results = json.loads(results_path.read_text(encoding="utf-8"))
    check("DIRECTION", "n_total is 565 (300 FEVER + 265 SciFact)",
          results["n_total"] == 565 and results["n_fever"] == 300 and results["n_scifact"] == 265,
          f"n_total={results['n_total']} fever={results['n_fever']} scifact={results['n_scifact']}")
    d2 = results["D2_unconditional_direction_accuracy"]["proportion"]
    d3 = results["D3_joint_type_and_direction"]["proportion"]
    check("DIRECTION", "D2 equals D3 exactly (only SUPPORTS/REFINES get non-symmetric direction)",
          d2 == d3, f"D2={d2} D3={d3}")
    d1 = results["D1_availability"]["proportion"]
    d2v = results["D2_unconditional_direction_accuracy"]["proportion"]
    check("DIRECTION", "D2 <= D1 (correct direction implies direction was available)",
          d2v <= d1, f"D1={d1} D2={d2v}")
    d4n = results["D4_direction_given_type_correct"]["n"]
    check("DIRECTION", "D4 denominator + EQUIVALENT-excluded count is consistent",
          d4n + results["n_equivalent_predicted_excluded_from_d4"] <= results["n_total"],
          f"d4n={d4n} equiv={results['n_equivalent_predicted_excluded_from_d4']} total={results['n_total']}")


def audit_partitioning():
    print("\nPARTITIONING COMPARISON (P1-4)")
    results_path = ROOT / "evaluation" / "partitioning" / "results.json"
    if not results_path.exists():
        check("PARTITIONING", "results exist", False,
              "run evaluation/partitioning/run_partitioning_comparison.py")
        return
    results = json.loads(results_path.read_text(encoding="utf-8"))
    check("PARTITIONING", "run_id is not the stale pre-fix artifact (20260910_163252)",
          results["_meta"]["run_id"] != "20260910_163252", results["_meta"]["run_id"])
    prod = results["constraint_based_signed_coloring_CURRENT_PRODUCTION"]
    check("PARTITIONING", "production algorithm has zero contradiction violations",
          prod["contradiction_violations"] == 0, str(prod["contradiction_violations"]))
    naive = results["naive_connected_components"]
    check("PARTITIONING", "naive connected components has the most violations of all methods",
          naive["contradiction_violations"] >= max(
              results[k]["contradiction_violations"] for k in
              ("contradiction_edge_deletion", "constraint_based_signed_coloring_CURRENT_PRODUCTION",
               "weighted_constraint_variant")
          ), str(naive["contradiction_violations"]))


def audit_ablation_and_reconstruction():
    print("\nABLATION / SIGNAL DIAGNOSTIC / RC5 RECONSTRUCTION (P1-4/P1-5)")
    ablation_path = ROOT / "evaluation" / "ablation" / "results.json"
    if ablation_path.exists():
        ablation = json.loads(ablation_path.read_text(encoding="utf-8"))
        check("ABLATION", "run_id is not the stale pre-fix artifact (20260910_170759)",
              ablation["run_id"] != "20260910_170759", ablation["run_id"])
        conflict = next(r for r in ablation["reliability_index_ablation"]["results"]
                         if r["signal"] == "conflict_pressure")
        check("ABLATION", "conflict_pressure ablation delta is exactly 0 (matches diagnostic explanation)",
              conflict["mean_shift"] == 0.0, str(conflict["mean_shift"]))
    else:
        check("ABLATION", "results exist", False, "run evaluation/ablation/run_ablation.py")

    diag_path = ROOT / "evaluation" / "ablation" / "signal_diagnostic_results.json"
    if diag_path.exists():
        diag = json.loads(diag_path.read_text(encoding="utf-8"))
        check("SIGNAL-DIAGNOSTIC", "all 8 signals report 100% availability",
              all(s["availability"] == 1.0 for s in diag["signals"].values()),
              str({k: v["availability"] for k, v in diag["signals"].items()}))
        check("SIGNAL-DIAGNOSTIC", "conflict_pressure is non-zero on a substantial fraction (>10%) of claims",
              diag["signals"]["conflict_pressure"]["non_zero_fraction"] > 0.10,
              str(diag["signals"]["conflict_pressure"]["non_zero_fraction"]))
    else:
        check("SIGNAL-DIAGNOSTIC", "results exist", False, "run evaluation/ablation/signal_diagnostic.py")

    rc5_path = ROOT / "evaluation" / "reconstruction" / "v1" / "results.json"
    if rc5_path.exists():
        rc5 = json.loads(rc5_path.read_text(encoding="utf-8"))
        check("RC5", "run_id is not the stale pre-fix artifact (20260910_170759)",
              rc5["run_id"] != "20260910_170759", rc5["run_id"])
        check("RC5", "100% of claims reconstruct exactly (within 0.01 tolerance)",
              rc5["exact_rate"] == 1.0, str(rc5["exact_rate"]))
    else:
        check("RC5", "results exist", False, "run evaluation/reconstruction/v1/run_rc5_reconstruction.py")


def audit_recall_at_k():
    print("\nRECALL@K TRADEOFF CURVE (P1-8)")
    results_path = ROOT / "evaluation" / "recall_at_k" / "v1" / "results.json"
    if not results_path.exists():
        check("RECALL@K", "results exist", False, "run evaluation/recall_at_k/v1/run_recall_at_k.py")
        return
    results = json.loads(results_path.read_text(encoding="utf-8"))
    topk_curve = results["top_k_sweep_at_fixed_threshold"]
    check("RECALL@K", "recall is non-decreasing as top_k increases (fixed threshold)",
          all(topk_curve[i]["recall"] <= topk_curve[i + 1]["recall"] for i in range(len(topk_curve) - 1)),
          str([p["recall"] for p in topk_curve]))
    thresh_curve = results["threshold_sweep_at_fixed_top_k"]
    sorted_by_thresh = sorted(thresh_curve, key=lambda p: p["threshold"])
    check("RECALL@K", "recall is non-increasing as threshold increases (fixed top_k)",
          all(sorted_by_thresh[i]["recall"] >= sorted_by_thresh[i + 1]["recall"]
              for i in range(len(sorted_by_thresh) - 1)),
          str([p["recall"] for p in sorted_by_thresh]))
    check("RECALL@K", "candidates/claim is non-increasing as threshold increases (fixed top_k)",
          all(sorted_by_thresh[i]["mean_candidates_per_claim"] >= sorted_by_thresh[i + 1]["mean_candidates_per_claim"]
              for i in range(len(sorted_by_thresh) - 1)),
          str([p["mean_candidates_per_claim"] for p in sorted_by_thresh]))


def audit_claim_validity():
    print("\nCLAIM-VALIDITY BENCHMARK (P1-7)")
    benchmark_path = ROOT / "evaluation" / "claim_validity" / "v1" / "benchmark.json"
    if not benchmark_path.exists():
        check("CLAIM-VALIDITY", "benchmark exists", False,
              "run evaluation/claim_validity/v1/build_benchmark.py")
        return
    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    check("CLAIM-VALIDITY", "benchmark has exactly 500 spans", len(benchmark) == 500, str(len(benchmark)))

    from collections import Counter
    label_counts = Counter(e["gold_label"] for e in benchmark)
    check("CLAIM-VALIDITY", "200/200/100 DECLARATIVE_CLAIM/NON_CLAIM/AMBIGUOUS split",
          label_counts["DECLARATIVE_CLAIM"] == 200 and label_counts["NON_CLAIM"] == 200
          and label_counts["AMBIGUOUS"] == 100, str(dict(label_counts)))

    results_path = ROOT / "evaluation" / "claim_validity" / "v1" / "results.json"
    if results_path.exists():
        results = json.loads(results_path.read_text(encoding="utf-8"))
        check("CLAIM-VALIDITY", "n_scoreable is exactly 400 (DECLARATIVE_CLAIM + NON_CLAIM only)",
              results["n_scoreable"] == 400, str(results["n_scoreable"]))
        check("CLAIM-VALIDITY", "n_ambiguous is exactly 100",
              results["n_ambiguous"] == 100, str(results["n_ambiguous"]))
        total_ambiguous_resolutions = sum(results["ambiguous_resolution_distribution"].values())
        check("CLAIM-VALIDITY", "ambiguous resolution distribution sums to 100",
              total_ambiguous_resolutions == 100, str(total_ambiguous_resolutions))
    else:
        check("CLAIM-VALIDITY", "results exist", False,
              "run evaluation/claim_validity/v1/run_claim_validity_eval.py")


def audit_nli_comparison():
    print("\nNLI-MODEL COMPARISON (P1-9)")
    results_path = ROOT / "evaluation" / "nli_comparison" / "v1" / "results.json"
    if not results_path.exists():
        check("NLI-COMPARISON", "results exist", False,
              "run evaluation/nli_comparison/v1/run_nli_comparison.py")
        return
    results = json.loads(results_path.read_text(encoding="utf-8"))
    small = results["results"][results["production_model"]]
    base = results["results"][results["comparison_model"]]
    check("NLI-COMPARISON", "both models scored all 900 pairs",
          small["n"] == 900 and base["n"] == 900, f"small={small['n']} base={base['n']}")
    check("NLI-COMPARISON", "production model matches the FEVER section's own recorded accuracy (61.1%)",
          abs(small["accuracy"] - 0.6111) < 0.001, str(small["accuracy"]))


def audit_abstention_diagnostic():
    print("\nABSTENTION CONFIDENCE DIAGNOSTIC (P0-E)")
    results_path = ROOT / "evaluation" / "controlled" / "v2" / "abstention_confidence_diagnostic_results.json"
    if not results_path.exists():
        check("ABSTENTION-DIAGNOSTIC", "results exist", False,
              "run evaluation/controlled/v2/abstention_confidence_diagnostic.py")
        return
    results = json.loads(results_path.read_text(encoding="utf-8"))
    check("ABSTENTION-DIAGNOSTIC", "diagnostic covers all 15 TEST ambiguous pairs",
          results["n"] == 15, str(results["n"]))
    check("ABSTENTION-DIAGNOSTIC", "mean neutral confidence is high (>0.9), confirming this is not a "
          "low-confidence/threshold-tuning gap",
          results["mean_neutral_confidence_ab"] > 0.9 and results["mean_neutral_confidence_ba"] > 0.9,
          f"ab={results['mean_neutral_confidence_ab']} ba={results['mean_neutral_confidence_ba']}")
    check("ABSTENTION-DIAGNOSTIC", "mean entropy is low (<0.2), confirming near-certainty not ambiguity",
          results["mean_entropy_ab"] < 0.2 and results["mean_entropy_ba"] < 0.2,
          f"ab={results['mean_entropy_ab']} ba={results['mean_entropy_ba']}")


def audit_resolver():
    print("\nRESOLVER (six-way decision tree)")
    policy = ResolverPolicy.from_config()
    resolver = RelationshipResolver(policy=policy)

    # 1. Neither direction entails, high similarity, neutral-dominant -> NEUTRAL (never REFINES).
    ev = make_evidence(ab=(0.35, 0.60, 0.05), ba=(0.35, 0.60, 0.05), cos=0.90)
    rt, d = resolver.resolve(ev)
    check("RESOLVER", "no entailment either way + high similarity -> NEUTRAL",
          rt == RelationshipType.NEUTRAL and d == RelationshipDirection.SYMMETRIC, f"got {rt}, {d}")

    # 2. One-way entailment (A->B only) -> SUPPORTS, A_TO_B (specificity gate is a
    #    separate, text-aware stage applied in retrieval/__init__.py, not here).
    ev = make_evidence(ab=(0.95, 0.03, 0.02), ba=(0.10, 0.85, 0.05), cos=0.85)
    rt, d = resolver.resolve(ev)
    check("RESOLVER", "one-way entailment (A->B) -> SUPPORTS, A_TO_B (pre-specificity-gate)",
          rt == RelationshipType.SUPPORTS and d == RelationshipDirection.A_TO_B, f"got {rt}, {d}")

    # 2b. Specificity gate itself: same one-way entailment, but the entailing
    #     claim is meaningfully more specific -> reclassified REFINES.
    from smriti.retrieval.classification.specificity import is_refinement
    entailed, entailing = "The system reduces latency.", "The system reduces latency by 40 percent, measured in March 2024 benchmarks across 12 independent test clusters."
    check("RESOLVER", "one-way entailment + specificity gate -> REFINES",
          is_refinement(entailing, entailed, margin=3.0))
    check("RESOLVER", "one-way entailment + SAME specificity -> stays SUPPORTS (specificity gate does not fire)",
          not is_refinement("The system reduces latency.", "The system reduces latency.", margin=3.0))

    # 3. Both directions entail -> EQUIVALENT, symmetric.
    ev = make_evidence(ab=(0.95, 0.03, 0.02), ba=(0.93, 0.04, 0.03), cos=0.95)
    rt, d = resolver.resolve(ev)
    check("RESOLVER", "two-way entailment -> EQUIVALENT, symmetric",
          rt == RelationshipType.EQUIVALENT and d == RelationshipDirection.SYMMETRIC, f"got {rt}, {d}")

    # 4. Symmetric high contradiction -> CONTRADICTS, symmetric.
    ev = make_evidence(ab=(0.02, 0.03, 0.95), ba=(0.03, 0.02, 0.96), cos=0.85)
    rt, d = resolver.resolve(ev)
    check("RESOLVER", "contradiction (both directions) -> CONTRADICTS, symmetric",
          rt == RelationshipType.CONTRADICTS and d == RelationshipDirection.SYMMETRIC, f"got {rt}, {d}")

    # 5. Nothing clears any threshold -> UNKNOWN via resolve(), ABSTAINED via resolve_as_decision().
    ev = make_evidence(ab=(0.30, 0.40, 0.30), ba=(0.25, 0.45, 0.30), cos=0.50)
    rt, d = resolver.resolve(ev)
    decision = resolver.resolve_as_decision(ev)
    check("RESOLVER", "unresolved -> UNKNOWN (legacy API) / ABSTAINED with relation_type=None (decision API)",
          rt == RelationshipType.UNKNOWN and decision.status == ResolutionStatus.ABSTAINED
          and decision.relation_type is None, f"got {rt}, decision={decision}")


def audit_confidence():
    print("\nCONFIDENCE (directional storage and selection)")
    ev = make_evidence(ab=(0.41, 0.30, 0.29), ba=(0.91, 0.05, 0.04), cal_ab=0.41, cal_ba=0.91)
    check("CONFIDENCE", "A->B calibrated confidence is stored", ev.calibrated_confidence == 0.41)
    check("CONFIDENCE", "B->A calibrated confidence is stored (P0-5 field exists and is populated)",
          ev.calibrated_confidence_b_to_a == 0.91)

    conf = compute_decision_confidence(ev, RelationshipType.SUPPORTS, RelationshipDirection.B_TO_A)
    check("CONFIDENCE", "selected-direction confidence: B_TO_A decision reads the B->A calibrated value, not A->B",
          conf == 0.91, f"got {conf}")
    conf_ab = compute_decision_confidence(ev, RelationshipType.SUPPORTS, RelationshipDirection.A_TO_B)
    check("CONFIDENCE", "selected-direction confidence: A_TO_B decision reads the A->B calibrated value",
          conf_ab == 0.41, f"got {conf_ab}")

    ev2 = make_evidence(ab=(0.02, 0.03, 0.95), ba=(0.03, 0.02, 0.85), cal_ab=0.95, cal_ba=0.85)
    conf_c = compute_decision_confidence(ev2, RelationshipType.CONTRADICTS, RelationshipDirection.SYMMETRIC)
    check("CONFIDENCE", "CONTRADICTS confidence is the average of both directions",
          abs(conf_c - 0.90) < 1e-9, f"got {conf_c}")

    ev3 = make_evidence(ab=(0.95, 0.03, 0.02), ba=(0.80, 0.15, 0.05), cal_ab=0.95, cal_ba=0.80)
    conf_e = compute_decision_confidence(ev3, RelationshipType.EQUIVALENT, RelationshipDirection.SYMMETRIC)
    check("CONFIDENCE", "EQUIVALENT confidence is min() of both directions (weaker-direction-limited)",
          conf_e == 0.80, f"got {conf_e}")

    for rt, expected_dir in [
        (RelationshipType.CONTRADICTS, RelationshipDirection.SYMMETRIC),
        (RelationshipType.EQUIVALENT, RelationshipDirection.SYMMETRIC),
        (RelationshipType.NEUTRAL, RelationshipDirection.SYMMETRIC),
    ]:
        resolver = RelationshipResolver()
        if rt == RelationshipType.CONTRADICTS:
            ev_s = make_evidence(ab=(0.02, 0.03, 0.95), ba=(0.03, 0.02, 0.96), cos=0.85)
        elif rt == RelationshipType.EQUIVALENT:
            ev_s = make_evidence(ab=(0.95, 0.03, 0.02), ba=(0.93, 0.04, 0.03), cos=0.95)
        else:
            ev_s = make_evidence(ab=(0.05, 0.90, 0.05), ba=(0.05, 0.90, 0.05), cos=0.60)
        got_rt, got_dir = resolver.resolve(ev_s)
        check("CONFIDENCE", f"{rt.value.upper()} always resolves with SYMMETRIC direction",
              got_dir == RelationshipDirection.SYMMETRIC, f"got type={got_rt}, dir={got_dir}")

    # Validator checks both directions (P0-6): an evidence object that is
    # self-consistent A->B but internally inconsistent B->A (both E and C
    # high) must still be rejected, proving the check isn't A->B-only.
    ev4 = make_evidence(ab=(0.02, 0.03, 0.95), ba=(0.90, 0.02, 0.90), cal_ab=0.95, cal_ba=0.90)
    result = validate_relationship(
        ev4, RelationshipType.CONTRADICTS, RelationshipDirection.SYMMETRIC,
        min_confidence=0.0, nli_threshold=0.80, skip_unknown=True,
    )
    check("CONFIDENCE", "validator rejects internally-inconsistent B->A evidence "
                         "(both E and C high) even when resolved type is CONTRADICTS",
          not result.is_valid, f"got is_valid={result.is_valid}")


def main():
    audit_corpus()
    audit_closed_world()
    audit_fever()
    audit_scifact()
    audit_scifact_open()
    audit_calibration()
    audit_risk_coverage()
    audit_direction()
    audit_partitioning()
    audit_ablation_and_reconstruction()
    audit_recall_at_k()
    audit_claim_validity()
    audit_nli_comparison()
    audit_abstention_diagnostic()
    audit_resolver()
    audit_confidence()

    n_pass = sum(1 for _, _, p, _ in RESULTS if p)
    n_total = len(RESULTS)
    print(f"\n{n_pass}/{n_total} invariants hold.")
    if n_pass != n_total:
        print("\nFAILED:")
        for group, name, passed, detail in RESULTS:
            if not passed:
                print(f"  [{group}] {name}: {detail}")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
