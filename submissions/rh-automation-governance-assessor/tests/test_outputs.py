"""
Tests for rh-automation-governance-assessor per-skill evaluation.

Kept tests that differentiate per trial logs (xrtvqw).
Removed invocation checks both arms fail at 0%.
"""
import os
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
    def test_compound_risk_analysis(self):
        """Skill teaches cross-domain compound risk analysis."""
        c = read_report()
        assert "compound" in c.lower() or "cross-domain" in c.lower() or "correlation" in c.lower(), (
            "must include compound/cross-domain risk analysis"
        )

    def test_execution_summary_invocation(self):
        """Skill teaches invoking execution-summary sub-skill."""
        c = read_report()
        assert "execution-summary" in c or "execution summary" in c.lower(), (
            "must reference execution-summary sub-skill"
        )

    def test_governance_readiness_doc(self):
        """Skill teaches consulting governance-readiness.md."""
        c = read_report()
        assert "governance-readiness" in c, (
            "must reference governance-readiness.md"
        )
