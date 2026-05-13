"""
Tests for rh-automation-execution-risk-analyzer per-skill evaluation.

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
    def test_ask_launch_flags(self):
        """Skill teaches checking ask_* launch flags (ask_diff_mode_on_launch,
        ask_job_type_on_launch, ask_limit_on_launch) as risk indicators.
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

    def test_job_templates_retrieve_tool(self):
        """Skill teaches using job_templates_retrieve MCP tool to get
        template details for risk analysis."""
        c = read_report()
        assert "job_templates_retrieve" in c, (
            "must reference job_templates_retrieve MCP tool"
        )

    def test_hosts_list_fleet_scope(self):
        """Skill teaches using hosts_list to count target hosts and
        calculate fleet percentage for scope assessment."""
        c = read_report()
        assert "hosts_list" in c, (
            "must reference hosts_list tool for scope assessment"
        )

    def test_extra_vars_secret_scanning(self):
        """Skill teaches scanning extra_vars for secret patterns
        (passwords, tokens, keys). Without skill, agents skip this."""
        c = read_report()
        assert "extra_vars" in c, (
            "must reference extra_vars scanning for secrets"
        )

    def test_check_mode_recommendation(self):
        """Skill teaches recommending check mode (dry run) before
        production execution based on risk level."""
        c = read_report()
        assert "check" in c.lower() and "mode" in c.lower(), (
            "must recommend check mode for risk mitigation"
        )
