"""
Tests for rh-developer-incident-triage per-skill evaluation.

Only differentiating tests kept — dead-weight tests where both
control and treatment pass have been removed.
"""
import os
import re
import pytest

REPORT = "/solution/report.md"


def read_report():
    if not os.path.exists(REPORT):
        pytest.fail(f"Required file not found: {REPORT}")
    with open(REPORT) as f:
        return f.read()


class TestBaseline:
    def test_report_exists(self):
        assert os.path.exists(REPORT), "report.md must exist"


class TestSkillDependent:
    def test_five_whys_present(self):
        """Skill teaches Five Whys methodology. Without skill, agents
        don't structure investigation this way."""
        c = read_report().lower()
        assert "five whys" in c or "5 whys" in c or "causal chain" in c, (
            "must use Five Whys methodology"
        )

    def test_multiple_why_levels(self):
        """Skill teaches tracing at least 3 levels of causal reasoning."""
        c = read_report().lower()
        why_count = len(re.findall(r'why[\s\?#\d]', c))
        assert why_count >= 3, "must trace at least 3 levels of 'why'"

    def test_exhaustive_verification(self):
        """Skill teaches exhaustive verification guardrail."""
        c = read_report().lower()
        assert "exhaustive" in c or "all resources" in c or "ownership chain" in c

    def test_contradicting_evidence(self):
        """Skill teaches checking for contradicting evidence."""
        c = read_report().lower()
        assert "contradict" in c or "alternative" in c or "ruled out" in c

    def test_confidence_score(self):
        """Skill teaches including a numeric confidence score (0.XX)."""
        c = read_report().lower()
        assert re.search(r'confidence[\s:]*[01]\.\d', c), (
            "must include numeric confidence score"
        )

    def test_due_diligence_dimensions(self):
        """Skill teaches the 8-dimension due diligence review framework."""
        c = read_report().lower()
        dimensions = [
            "causal completeness", "target accuracy",
            "evidence sufficiency", "alternative hypothes",
            "scope completeness", "proportionality",
            "regression", "confidence calibration",
        ]
        found = sum(1 for d in dimensions if d in c)
        assert found >= 4, (
            f"must address at least 4 of 8 due diligence dimensions, found {found}"
        )
