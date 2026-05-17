"""
Tests for rh-sre-playbook-executor per-skill evaluation.

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
    def test_dry_run_check_mode(self):
        """SKILL Phase 3: dry-run uses job_type 'check' mode."""
        c = read_report().lower()
        has_dry = any(t in c for t in [
            "dry-run", "dry run", "check mode", "check run",
            "job_type: check", 'job_type: "check"',
        ])
        assert has_dry, "must describe dry-run / check mode"

    def test_production_run_mode(self):
        """SKILL Phase 4: production uses job_type 'run'."""
        c = read_report().lower()
        has_run = any(t in c for t in [
            "job_type: run", 'job_type: "run"',
            "production execution", "production run",
        ])
        assert has_run, "must describe production execution with job_type run"

    def test_git_flow_awareness(self):
        """SKILL: Git Flow is MANDATORY before launching — commit, push, sync."""
        c = read_report().lower()
        has_git = any(t in c for t in [
            "git flow", "project sync", "scm sync",
        ])
        assert has_git, "must address Git Flow / project sync before execution"

    def test_template_selection_scenarios(self):
        """SKILL defines 3 template scenarios: exact, different path, no template."""
        c = read_report().lower()
        has_scenario = any(t in c for t in [
            "exact match", "different playbook",
            "template selection", "job-template-creator",
        ])
        assert has_scenario, "should describe template selection approach"

    def test_specific_aap_template_from_mcp(self):
        """AAP MCP has specific templates (CVE Remediation Kernel/Package/Generic)."""
        c = read_report().lower()
        has_template = any(t in c for t in [
            "kernel update", "package update", "cve remediation",
            "template 10", "template 11", "template 12",
        ])
        assert has_template, "should reference specific AAP templates from MCP"

    def test_launch_tool_usage(self):
        """SKILL: job_templates_launch_retrieve for launching jobs."""
        c = read_report().lower()
        has_launch = any(t in c for t in [
            "job_templates_launch", "launch_retrieve",
        ])
        assert has_launch, "should reference job_templates_launch_retrieve tool"
