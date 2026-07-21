"""
evidence_model.py — Scientific Evidence Model (Section 12.9).

Evidence Lifecycle:
    Requirement → Principle → ADR → Implementation → Verification
    → Validation → Metrics → Statistical Analysis → Conclusion → Research Claim
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class EvidenceChainLink:
    level: str
    identifier: str
    description: str
    artifact_path: Optional[str] = None


@dataclass(frozen=True)
class EvidenceChain:
    chain_id: str
    research_claim_id: str
    links: tuple

    @property
    def is_complete(self) -> bool:
        return len(self.links) >= 5

    @property
    def has_statistical_analysis(self) -> bool:
        return any(l.level == "statistical_analysis" for l in self.links)

    @property
    def has_adr(self) -> bool:
        return any(l.level == "adr" for l in self.links)


def build_evidence_chain(
    chain_id: str,
    research_claim_id: str,
    requirement_id: str,
    principle_numbers: list,
    adr_ids: list,
    implementation_modules: list,
    verification_rule_ids: list,
    validation_rule_ids: list,
    metric_names: list,
    statistical_analysis_ids: list,
    conclusion: str,
) -> EvidenceChain:
    links = []
    links.append(EvidenceChainLink("requirement", requirement_id, f"Requirement: {requirement_id}"))
    for pn in principle_numbers:
        links.append(EvidenceChainLink("principle", f"P-{pn}", f"Principle {pn}"))
    for adr_id in adr_ids:
        links.append(EvidenceChainLink("adr", adr_id, f"ADR {adr_id}"))
    for mod in implementation_modules:
        links.append(EvidenceChainLink("implementation", mod, f"Module: {mod}"))
    for rule_id in verification_rule_ids:
        links.append(EvidenceChainLink("verification", rule_id, f"Rule: {rule_id}"))
    for rule_id in validation_rule_ids:
        links.append(EvidenceChainLink("validation", rule_id, f"Validation: {rule_id}"))
    for metric in metric_names:
        links.append(EvidenceChainLink("evaluation", metric, f"Metric: {metric}"))
    for sa_id in statistical_analysis_ids:
        links.append(EvidenceChainLink("statistical_analysis", sa_id, f"SA: {sa_id}"))
    links.append(EvidenceChainLink("conclusion", chain_id, conclusion))
    return EvidenceChain(chain_id=chain_id, research_claim_id=research_claim_id, links=tuple(links))