"""
Tests for rh-automation-governance-executor per-skill evaluation.

Kept sub-skill invocations treatment passes more often; removed forensic (both 100%).
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
