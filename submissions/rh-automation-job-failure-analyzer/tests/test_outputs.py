"""
Tests for rh-automation-job-failure-analyzer per-skill evaluation.

Reduced from 7 to 5 tests. Removed job_troubleshooting_doc and
host_fact_inspector_next_step (dead-weight: both agents pass).
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
    def test_jobs_job_events_list_tool(self):
        """Skill teaches using jobs_job_events_list MCP tool to extract
        failure events. Without skill, agents describe generic log analysis."""
        c = read_report()
        assert "jobs_job_events_list" in c or "job_events_list" in c, (
            "must reference jobs_job_events_list MCP tool"
        )

    def test_jobs_job_host_summaries_tool(self):
        """Skill teaches jobs_job_host_summaries_list for per-host breakdown.
        Without skill, agents don't know this tool exists."""
        c = read_report()
        assert "host_summaries" in c or "host summaries" in c.lower(), (
            "must reference jobs_job_host_summaries_list MCP tool"
        )

    def test_runner_on_failed_event(self):
        """Skill teaches filtering for runner_on_failed and runner_on_unreachable
        event types. Without skill, agents don't know AAP event taxonomy."""
        c = read_report()
        assert "runner_on_failed" in c or "runner_on_unreachable" in c, (
            "must reference runner_on_failed or runner_on_unreachable event types"
        )

    def test_event_data_fields(self):
        """Skill teaches extracting event_data.res.msg and event_data.task_action
        from failure events. Without skill, agents skip structured event parsing."""
        c = read_report().lower()
        assert "event_data" in c or "res.msg" in c or "task_action" in c, (
            "must reference event_data fields (res.msg, task_action)"
        )
