"""
Tests for rh-automation-forensic-troubleshooter per-skill evaluation.

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
    def test_job_failure_analyzer_invocation(self):
        """Skill teaches invoking job-failure-analyzer sub-skill for
        structured event extraction. Without skill, agents do ad-hoc analysis."""
        c = read_report()
        assert "job-failure-analyzer" in c or "failure-analyzer" in c, (
            "must reference job-failure-analyzer sub-skill invocation"
        )

    def test_host_fact_inspector_invocation(self):
        """Skill teaches invoking host-fact-inspector sub-skill to
        correlate failures with host system state."""
        c = read_report()
        assert "host-fact-inspector" in c or "host fact" in c.lower(), (
            "must reference host-fact-inspector sub-skill"
        )

    def test_resolution_advisor_invocation(self):
        """Skill teaches invoking resolution-advisor sub-skill for
        Red Hat documentation-backed resolution steps."""
        c = read_report()
        assert "resolution-advisor" in c or "resolution advisor" in c.lower(), (
            "must reference resolution-advisor sub-skill"
        )

    def test_job_troubleshooting_doc_consultation(self):
        """Skill teaches consulting job-troubleshooting.md for event
        parsing patterns and failure classification."""
        c = read_report()
        assert "job-troubleshooting" in c or "job troubleshooting" in c.lower(), (
            "must reference job-troubleshooting.md consultation"
        )
