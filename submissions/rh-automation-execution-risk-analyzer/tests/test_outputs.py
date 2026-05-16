"""
Tests for rh-automation-execution-risk-analyzer per-skill evaluation.

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
        """Skill teaches consulting execution-governance.md before any
        risk analysis. Without skill, agents skip structured governance
        reference."""
        c = read_report().lower()
        assert "execution-governance" in c, (
            "must reference execution-governance.md document"
        )

    def test_ask_launch_flags(self):
        """Skill teaches checking ask_* launch flags as risk indicators.
        Without skill, agents don't check these AAP-specific flags."""
        c = read_report()
        has_ask = any(f in c for f in [
            "ask_diff_mode_on_launch",
            "ask_job_type_on_launch",
            "ask_limit_on_launch",
            "ask_variables_on_launch",
        ])
        assert has_ask, (
            "must check ask_*_on_launch flags as risk indicators"
        )

    def test_inventories_list_tool(self):
        """Skill teaches using inventories_list to enumerate available
        inventories for scope assessment. Without skill, agents only
        use job_templates_retrieve."""
        c = read_report()
        assert "inventories_list" in c or "inventories" in c, (
            "must reference inventories_list for scope assessment"
        )

    def test_job_history_analysis(self):
        """Skill teaches querying jobs_list to check recent execution
        history for failure patterns. Without skill, agents assess
        risk without operational context."""
        c = read_report()
        assert "jobs_list" in c or "job history" in c.lower() or "recent job" in c.lower(), (
            "must analyze job history for failure patterns"
        )

    def test_governed_job_launcher_next_step(self):
        """Skill teaches routing to governed-job-launcher as the next
        step after risk classification. Without skill, agents don't
        know the execution pipeline."""
        c = read_report().lower()
        assert "governed-job-launcher" in c or "job-launcher" in c, (
            "must reference governed-job-launcher as next step"
        )

    def test_adaptive_risk_enhancement(self):
        """Skill teaches adaptive risk enhancement rules that can
        escalate risk level based on operational context (e.g., recent
        failures, shell modules, missing notifications)."""
        c = read_report().lower()
        assert "adaptive" in c or "enhancement" in c or "escalat" in c or (
            "upgrade" in c and "risk" in c
        ), "must describe adaptive risk enhancement or escalation rules"
