"""
Tests for rh-automation-governance-executor per-skill evaluation.

Reduced to 3 strongest differentiating tests. Removed tests that
cause high treatment variance (execution_governance_doc,
execution_summary_final_step, governed_job_launcher_invocation).
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
    def test_execution_risk_analyzer_invocation(self):
        """Skill teaches invoking execution-risk-analyzer before job launch."""
        c = read_report()
        assert "execution-risk-analyzer" in c or "risk-analyzer" in c, (
            "must reference execution-risk-analyzer sub-skill"
        )

    def test_risk_level_classification(self):
        """Skill teaches classifying risk as CRITICAL/HIGH/MEDIUM/LOW
        with different governance controls per level."""
        c = read_report()
        levels = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        found = sum(1 for l in levels if l in c)
        assert found >= 2, (
            "must classify execution risk level (CRITICAL/HIGH/MEDIUM/LOW)"
        )

    def test_check_mode_governance(self):
        """Skill teaches running check mode (dry-run) before production
        execution for CRITICAL/HIGH risk levels."""
        c = read_report().lower()
        assert "check mode" in c or "dry-run" in c or "dry run" in c, (
            "must describe check mode / dry-run governance step"
        )
