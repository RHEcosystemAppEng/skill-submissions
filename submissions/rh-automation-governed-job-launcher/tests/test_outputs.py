"""
Tests for rh-automation-governed-job-launcher per-skill evaluation.

Only differentiating tests kept — dead-weight tests where both
control and treatment pass have been removed.
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
    def test_execution_governance_doc(self):
        """Skill teaches consulting execution-governance.md before any MCP
        calls. Without skill, agents skip document consultation."""
        c = read_report().lower()
        assert "execution-governance" in c, (
            "must reference execution-governance.md document"
        )

    def test_phased_rollout(self):
        """Skill teaches phased rollout strategy: canary -> 25% -> full
        production. Without skill, agents execute on all hosts at once."""
        c = read_report().lower()
        assert "canary" in c or "phased" in c or "25%" in c or "rolling" in c, (
            "must describe phased rollout strategy (canary/25%/full)"
        )

    def test_host_summary_columns(self):
        """Skill teaches interpreting host summary columns: failures, dark,
        changed, skipped from jobs_job_host_summaries_list. Without skill,
        agents only check pass/fail."""
        c = read_report().lower()
        cols = ["dark", "failures", "changed", "skipped"]
        found = sum(1 for col in cols if col in c)
        assert found >= 2, (
            "must reference host summary columns (dark/failures/changed/skipped)"
        )

    def test_execution_risk_analyzer_prerequisite(self):
        """Skill teaches that execution-risk-analyzer results are a
        prerequisite for governed launches. Without skill, agents launch
        without prior risk assessment."""
        c = read_report().lower()
        assert "execution-risk-analyzer" in c or "risk-analyzer" in c or (
            "risk" in c and "prior" in c and "analys" in c
        ), "must reference execution-risk-analyzer as prerequisite"

    def test_diff_mode_for_critical(self):
        """Skill teaches using diff_mode for CRITICAL/HIGH risk check-mode
        runs to show what would change. Without skill, agents use plain
        check mode without diff insight."""
        c = read_report().lower()
        assert "diff_mode" in c or "diff mode" in c, (
            "must reference diff_mode for check-mode enrichment"
        )

    def test_forensic_troubleshooter_escalation(self):
        """Skill teaches escalating to forensic-troubleshooter when recent
        failures exist. Without skill, agents don't know the skill chain."""
        c = read_report().lower()
        assert "forensic-troubleshooter" in c or "forensic" in c, (
            "must reference forensic-troubleshooter escalation path"
        )
