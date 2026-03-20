"""
Infrastructure Risk Scoring Model
Computes a composite risk score (0-100) from detected defects.
Rule-based with configurable weights — replace with ML model in v2.
"""
from typing import List


SEVERITY_WEIGHTS = {
    "critical": 1.0,
    "high": 0.7,
    "medium": 0.4,
    "low": 0.1,
}

DEFECT_TYPE_MULTIPLIERS = {
    "broken_component": 1.5,
    "missing_component": 1.5,
    "spalling": 1.3,
    "crack": 1.2,
    "delamination": 1.1,
    "corrosion": 1.0,
    "erosion": 0.9,
    "discoloration": 0.6,
}


class RiskScoringModel:

    def compute_risk_score(self, defects: List[dict]) -> float:
        if not defects:
            return 0.0

        weighted_scores = []
        for d in defects:
            severity_weight = SEVERITY_WEIGHTS.get(d.get("severity", "low"), 0.1)
            type_mult = DEFECT_TYPE_MULTIPLIERS.get(d.get("type", ""), 1.0)
            confidence = d.get("confidence", 0.5)
            score = severity_weight * type_mult * confidence
            weighted_scores.append(score)

        if not weighted_scores:
            return 0.0

        # Combine: max defect score + average contribution
        max_score = max(weighted_scores)
        avg_score = sum(weighted_scores) / len(weighted_scores)
        combined = (max_score * 0.6 + avg_score * 0.4)

        # Apply defect count penalty
        count_penalty = min(len(defects) * 0.02, 0.3)
        final = min(combined + count_penalty, 1.0)

        return round(final * 100, 2)

    def generate_maintenance_priority(self, risk_score: float) -> str:
        if risk_score >= 80:
            return "IMMEDIATE — Halt operations and inspect within 24 hours"
        elif risk_score >= 60:
            return "HIGH — Schedule inspection within 7 days"
        elif risk_score >= 40:
            return "MEDIUM — Schedule inspection within 30 days"
        elif risk_score >= 20:
            return "LOW — Include in next routine maintenance cycle"
        else:
            return "MINIMAL — Monitor at standard inspection intervals"

    def generate_summary(self, defects: List[dict], risk_score: float) -> str:
        if not defects:
            return "No defects detected. Infrastructure appears to be in good condition."

        critical = [d for d in defects if d.get("severity") == "critical"]
        high = [d for d in defects if d.get("severity") == "high"]

        parts = [f"Detected {len(defects)} defect(s) with a risk score of {risk_score:.0f}/100."]
        if critical:
            types = list({d['type'] for d in critical})
            parts.append(f"{len(critical)} critical issue(s): {', '.join(types)}.")
        if high:
            types = list({d['type'] for d in high})
            parts.append(f"{len(high)} high-severity issue(s): {', '.join(types)}.")

        return " ".join(parts)


risk_model = RiskScoringModel()
