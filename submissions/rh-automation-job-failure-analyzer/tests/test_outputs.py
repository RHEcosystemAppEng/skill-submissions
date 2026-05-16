"""
Tests for rh-automation-job-failure-analyzer per-skill evaluation.

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
    def test_job_troubleshooting_doc(self):
        """Skill teaches consulting job-troubleshooting.md for error
        classification patterns. Without skill, agents skip the
        structured troubleshooting reference."""
        c = read_report().lower()
        assert "job-troubleshooting" in c, (
            "must reference job-troubleshooting.md document"
        )

    def test_runner_event_types(self):
        """Skill teaches filtering for specific runner event types:
        runner_on_failed, runner_on_unreachable, playbook_on_stats.
        Without skill, agents describe events generically."""
        c = read_report()
        events = [
            "runner_on_failed", "runner_on_unreachable",
            "playbook_on_stats",
        ]
        found = sum(1 for e in events if e in c)
        assert found >= 1, (
            "must reference specific runner event types "
            "(runner_on_failed/runner_on_unreachable/playbook_on_stats)"
        )

    def test_event_data_fields(self):
        """Skill teaches extracting specific event_data fields:
        event_data.res.msg, event_data.task_action. Without skill,
        agents describe error messages without structured field paths."""
        c = read_report()
        assert "event_data" in c or "task_action" in c or "res.msg" in c, (
            "must reference event_data fields (res.msg, task_action)"
        )

    def test_dark_hosts_concept(self):
        """Skill teaches 'dark' hosts as unreachable in host summaries,
        distinct from 'failures'. Without skill, agents conflate
        unreachable and failed hosts."""
        c = read_report().lower()
        assert "dark" in c, (
            "must reference 'dark' hosts (unreachable) from host summaries"
        )

    def test_host_fact_inspector_next_step(self):
        """Skill teaches routing to host-fact-inspector as the next
        forensic step. Without skill, agents don't know the pipeline."""
        c = read_report().lower()
        assert "host-fact-inspector" in c or "host fact" in c, (
            "must reference host-fact-inspector as next forensic step"
        )

    def test_error_classification_reference(self):
        """Skill teaches using the error-classification.md reference for
        structured error categorization. Without skill, agents classify
        errors ad-hoc."""
        c = read_report().lower()
        assert "error-classification" in c or "classification" in c, (
            "must reference error-classification document or framework"
        )
