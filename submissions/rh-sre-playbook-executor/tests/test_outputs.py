"""
Tests for rh-sre__playbook-executor skill evaluation.

Tests check for knowledge from the skill package (SKILL.md +
references/02-error-handling-guide.md + 05-git-flow-prompts.md)
that is only available to the treatment agent.
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

    def test_mentions_playbook(self):
        content = read_report().lower()
        assert "playbook" in content

    def test_report_has_structure(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"


class TestSkillDependent:

    def test_git_flow_sequence(self):
        """Skill teaches mandatory Git Flow: write -> git add -> commit
        -> push -> await 'sync complete' BEFORE any job launch.
        Without skill, agents launch directly from local files."""
        c = read_report().lower()
        has_git = "git" in c
        has_sync = "sync" in c
        has_commit = "commit" in c
        assert has_git and has_sync and has_commit

    def test_dry_run_check_mode(self):
        """Skill teaches dry-run via job_type: 'check' parameter in
        job_templates_launch_retrieve. Without skill, agents run
        --check as CLI flag or skip dry-run."""
        c = read_report()
        has_check = "check" in c.lower()
        has_job_type = "job_type" in c
        assert has_check and has_job_type

    def test_job_polling_mechanism(self):
        """Skill teaches polling via jobs_retrieve every 2 seconds
        and events via jobs_job_events_list. Without skill, agents
        wait indefinitely or check once."""
        c = read_report()
        has_jobs_retrieve = "jobs_retrieve" in c
        has_events = "job_events_list" in c or "events" in c.lower()
        assert has_jobs_retrieve and has_events

    def test_host_summaries(self):
        """Skill teaches jobs_job_host_summaries_list for per-host
        results. Without skill, agents parse stdout manually."""
        c = read_report()
        assert "host_summaries" in c or "job_host_summaries" in c

    def test_absolute_write_paths(self):
        """Skill teaches write paths must be absolute — relative
        paths fail silently. Without skill, agents use relative
        paths like 'playbooks/...' without anchoring."""
        c = read_report()
        has_absolute = "/playbooks/" in c or "absolute" in c.lower()
        assert has_absolute

    def test_no_override_at_launch(self):
        """Skill teaches AAP runs from synced project only — no
        playbook override at launch time. Without skill, agents
        try to pass playbook content as launch parameter."""
        c = read_report().lower()
        has_sync_required = any(t in c for t in [
            "synced project", "project sync", "sync complete",
            "git flow", "no override",
        ])
        assert has_sync_required

    def test_mcp_aap_validator(self):
        """Skill teaches running mcp-aap-validator BEFORE execution.
        Without skill, agents proceed without validating AAP
        availability."""
        c = read_report()
        has_validator = "mcp-aap-validator" in c or "aap-validator" in c
        has_result = any(t in c for t in ["PASSED", "FAILED", "PARTIAL"])
        assert has_validator or has_result
