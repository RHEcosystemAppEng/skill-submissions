"""
Tests for rh-automation-job-failure-analyzer per-skill evaluation.

Kept tests where treatment outperforms control (548g5 trial logs).
Removed runner_event_types and error_classification (control passes 100%).
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
        """Skill teaches consulting job-troubleshooting.md."""
        c = read_report().lower()
        assert "job-troubleshooting" in c, (
            "must reference job-troubleshooting.md document"
        )

    def test_dark_hosts_concept(self):
        """Skill teaches 'dark' hosts distinct from failures."""
        c = read_report().lower()
        assert "dark" in c, (
            "must reference 'dark' hosts (unreachable) from host summaries"
        )

    def test_host_fact_inspector_next_step(self):
        """Skill teaches routing to host-fact-inspector next."""
        c = read_report().lower()
        assert "host-fact-inspector" in c or "host fact" in c, (
            "must reference host-fact-inspector as next forensic step"
        )
