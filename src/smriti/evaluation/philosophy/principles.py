"""
principles.py — 8 Scientific Validation Principles (Section 12.1).

The 8 principles:
    1. Evidence over Assertion
    2. Repeatability
    3. Reproducibility
    4. Traceability
    5. Objectivity
    6. Determinism
    7. Transparency
    8. Progressive Validation
"""

from __future__ import annotations
from typing import List
from smriti.core.models import ValidationPrinciple

VALIDATION_PRINCIPLES: List[ValidationPrinciple] = [
    ValidationPrinciple(1, "Evidence over Assertion",
        "Every architectural or scientific claim must be supported by "
        "measurable empirical evidence. Assertions without evidence "
        "are excluded from all reports."),
    ValidationPrinciple(2, "Repeatability",
        "Independent executions under identical conditions shall produce "
        "identical evaluation outcomes. Non-determinism is explicitly "
        "documented and quantified."),
    ValidationPrinciple(3, "Reproducibility",
        "Independent researchers shall be capable of reproducing published "
        "experimental results using documented artifacts, configurations, "
        "and methodology."),
    ValidationPrinciple(4, "Traceability",
        "Every reported metric shall be traceable back to its originating "
        "requirement, architectural decision, implementation module, and "
        "experimental configuration."),
    ValidationPrinciple(5, "Objectivity",
        "Evaluation shall rely on predefined acceptance criteria rather "
        "than subjective judgement. Criteria are established before "
        "experiments are executed."),
    ValidationPrinciple(6, "Determinism",
        "Controlled experiments shall eliminate unnecessary sources of "
        "non-determinism whenever possible. Random seeds are fixed, "
        "documented, and included in all experiment manifests."),
    ValidationPrinciple(7, "Transparency",
        "Evaluation methodology, assumptions, datasets, configurations, "
        "and limitations shall remain explicitly documented and permanently "
        "archived with the results they produced."),
    ValidationPrinciple(8, "Progressive Validation",
        "Architectural correctness shall be established incrementally, "
        "beginning with fundamental invariants and progressing toward "
        "complete system evaluation. No level may be certified without "
        "its predecessors."),
]

def get_principle(number: int) -> ValidationPrinciple:
    for p in VALIDATION_PRINCIPLES:
        if p.number == number:
            return p
    raise KeyError(f"Principle {number} not defined")