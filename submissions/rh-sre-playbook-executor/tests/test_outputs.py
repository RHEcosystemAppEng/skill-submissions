"""
Tests for rh-sre playbook-executor skill evaluation.
Tests check for the specific execution workflow from SKILL.md.
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

    def test_report_has_content(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"

    def test_mentions_playbook(self):
        content = read_report().lower()
        assert "playbook" in content, "report should mention playbook execution"


class TestSkillDependent:
    def test_dry_run_check_mode(self):
        """SKILL Phase 3: dry-run uses job_type 'check' mode before production execution."""
        c = read_report().lower()
        has_dry = any(t in c for t in [
            "dry-run", "dry run", "check mode", "check run",
            'job_type.*check', "job_type: check", "job_type: \"check\"",
        ])
        assert has_dry, (
            "must describe dry-run / check mode execution (SKILL Phase 3)"
        )

    def test_production_run_mode(self):
        """SKILL Phase 4: production uses job_type 'run' for actual changes."""
        c = read_report().lower()
        has_run = any(t in c for t in [
            "job_type: run", "job_type: \"run\"", 'job_type.*run',
            "actual execution", "production execution", "production run",
        ])
        assert has_run, (
            "must describe production execution with job_type run (SKILL Phase 4)"
        )

    def test_git_flow_awareness(self):
        """SKILL: Git Flow is MANDATORY before launching - commit, push, sync.
        Without it, AAP executes the WRONG playbook."""
        c = read_report().lower()
        has_git = any(t in c for t in [
            "git flow", "git commit", "git push",
            "sync", "project sync", "scm sync",
            "committed", "pushed",
        ])
        assert has_git, (
            "must address Git Flow / project sync before execution "
            "(SKILL: MANDATORY before launch)"
        )

    def test_template_selection_scenarios(self):
        """SKILL defines 3 template scenarios: exact match, different path, no template."""
        c = read_report().lower()
        has_scenario = any(t in c for t in [
            "exact match", "same playbook", "different playbook",
            "compatible", "scenario", "template selection",
            "create.*template", "job-template-creator",
        ])
        assert has_scenario, (
            "should describe template selection approach (SKILL Scenarios 1/2/3)"
        )

    def test_human_confirmation_before_execution(self):
        """SKILL: ONLY execute if user explicitly confirms. HITL required."""
        c = read_report().lower()
        has_confirm = any(t in c for t in [
            "confirm", "approval", "user confirm",
            "human-in-the-loop", "hitl", "explicit",
            "proceed", "abort",
        ])
        assert has_confirm, (
            "must require human confirmation before production execution (SKILL HITL)"
        )

    def test_job_monitoring(self):
        """SKILL: poll jobs_retrieve every 2 seconds, use jobs_job_events_list."""
        c = read_report().lower()
        has_monitor = any(t in c for t in [
            "monitor", "polling", "poll", "jobs_retrieve",
            "job status", "job_events", "progress",
        ])
        assert has_monitor, (
            "must describe job monitoring / status polling (SKILL Phase 4.3)"
        )

    def test_per_host_results(self):
        """SKILL: jobs_job_host_summaries_list for per-host results."""
        c = read_report().lower()
        has_host = any(t in c for t in [
            "per-host", "per host", "host summar",
            "host_summaries", "host result",
            "succeeded", "failed", "unreachable",
        ])
        assert has_host, (
            "must include per-host execution results (SKILL Phase 4.4)"
        )

    def test_specific_aap_template_from_mcp(self):
        """AAP MCP has templates 10/11/12 (CVE Remediation - Kernel/Package/Generic)."""
        c = read_report().lower()
        has_template = any(t in c for t in [
            "kernel update", "package update", "cve remediation",
            "template 10", "template 11", "template 12",
            "id: 10", "id: 11", "id 10", "id 11",
        ])
        assert has_template, (
            "should reference specific AAP templates from MCP environment"
        )

    def test_launch_tool_usage(self):
        """SKILL: job_templates_launch_retrieve for launching jobs."""
        c = read_report().lower()
        has_launch = any(t in c for t in [
            "job_templates_launch", "launch_retrieve",
            "launch job", "launch the job",
        ])
        assert has_launch, (
            "should reference job_templates_launch_retrieve tool (SKILL Phase 3/4)"
        )

    def test_failure_handling(self):
        """SKILL: handle failures with retry, rollback, escalation."""
        c = read_report().lower()
        has_failure = any(t in c for t in [
            "rollback", "retry", "relaunch", "escalat",
            "failure handling", "if.*fail", "error handling",
        ])
        assert has_failure, (
            "must include failure handling guidance (retry/rollback/escalation)"
        )
