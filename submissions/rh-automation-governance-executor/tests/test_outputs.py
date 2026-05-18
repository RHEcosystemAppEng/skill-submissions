"""
Tests for rh-automation-governance-executor per-skill evaluation.

Skill orchestrates governed job execution: risk analysis -> check mode ->
approval -> phased rollout. Invokes sub-skills and applies governance
controls based on risk level (CRITICAL/HIGH/MEDIUM/LOW).
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

    def test_governed_job_launcher_invocation(self):
        """Skill teaches invoking governed-job-launcher for check-then-run."""
        c = read_report()
        assert "governed-job-launcher" in c or "job-launcher" in c, (
            "must reference governed-job-launcher sub-skill"
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

    def test_execution_governance_doc(self):
        """Skill teaches consulting execution-governance.md for
        governance policies. Without skill, agents skip documentation."""
        c = read_report().lower()
        assert "execution-governance" in c, (
            "must reference execution-governance.md document"
        )

    def test_execution_summary_final_step(self):
        """Skill teaches invoking execution-summary as the final step
        after governed execution completes."""
        c = read_report()
        assert "execution-summary" in c or "execution summary" in c.lower(), (
            "must reference execution-summary as final pipeline step"
        )
