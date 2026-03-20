"""
Tests for inspection service and risk scoring.
Run with: pytest tests/ -v
"""
import pytest
from app.models.models import DefectSeverity
from app.services.ai.inspection_service import InspectionService
from ai_service.app.models.risk_scoring import RiskScoringModel


class TestRiskScoring:
    def setup_method(self):
        self.model = RiskScoringModel()

    def test_empty_defects_returns_zero(self):
        assert self.model.compute_risk_score([]) == 0.0

    def test_single_critical_defect(self):
        defects = [{"type": "broken_component", "severity": "critical", "confidence": 0.95}]
        score = self.model.compute_risk_score(defects)
        assert score > 80

    def test_low_severity_defect(self):
        defects = [{"type": "discoloration", "severity": "low", "confidence": 0.5}]
        score = self.model.compute_risk_score(defects)
        assert score < 20

    def test_multiple_defects_higher_than_single(self):
        single = [{"type": "crack", "severity": "medium", "confidence": 0.7}]
        multiple = [
            {"type": "crack", "severity": "medium", "confidence": 0.7},
            {"type": "corrosion", "severity": "high", "confidence": 0.8},
            {"type": "spalling", "severity": "critical", "confidence": 0.9},
        ]
        assert self.model.compute_risk_score(multiple) > self.model.compute_risk_score(single)

    def test_score_bounded_0_100(self):
        defects = [
            {"type": "broken_component", "severity": "critical", "confidence": 1.0}
            for _ in range(50)
        ]
        score = self.model.compute_risk_score(defects)
        assert 0 <= score <= 100

    def test_maintenance_priority_critical(self):
        priority = self.model.generate_maintenance_priority(85)
        assert "IMMEDIATE" in priority

    def test_maintenance_priority_low(self):
        priority = self.model.generate_maintenance_priority(10)
        assert "MINIMAL" in priority
