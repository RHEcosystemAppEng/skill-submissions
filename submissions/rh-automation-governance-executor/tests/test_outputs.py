"""
Tests for rh-automation-governance-executor per-skill evaluation.

Only differentiating tests kept — dead-weight tests where both
control and treatment pass 3/3 have been removed.
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
        """Skill teaches invoking execution-risk-analyzer sub-skill before
        any job launch. Without skill, agents skip risk analysis."""
        c = read_report()
        assert "execution-risk-analyzer" in c or "risk-analyzer" in c, (
            "must reference execution-risk-analyzer sub-skill"
        )

    def test_governed_job_launcher_invocation(self):
        """Skill teaches invoking governed-job-launcher sub-skill for
        the actual check-mode-then-run sequence."""
        c = read_report()
        assert "governed-job-launcher" in c or "job-launcher" in c, (
            "must reference governed-job-launcher sub-skill"
        )

    def test_execution_governance_doc(self):
        """Skill teaches consulting execution-governance.md for risk
        classification and check mode requirements."""
        c = read_report()
        assert "execution-governance" in c, (
            "must reference execution-governance.md"
        )

    def test_forensic_troubleshooter_on_failure(self):
        """Skill teaches triggering forensic-troubleshooter sub-skill
        automatically when job execution fails."""
        c = read_report()
        assert "forensic-troubleshooter" in c or "forensic" in c.lower(), (
            "must reference forensic-troubleshooter for failure handling"
        )
