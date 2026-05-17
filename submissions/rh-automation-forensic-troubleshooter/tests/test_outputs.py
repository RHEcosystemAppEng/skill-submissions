"""
Tests for rh-automation-forensic-troubleshooter per-skill evaluation.

Kept checks treatment passes more often; removed host-fact (both 100%) and
job-failure-analyzer (both 0%).
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
    def test_job_troubleshooting_doc_consultation(self):
        """Skill teaches consulting job-troubleshooting.md."""
        c = read_report()
        assert "job-troubleshooting" in c or "job troubleshooting" in c.lower(), (
            "must reference job-troubleshooting.md consultation"
        )

    def test_resolution_advisor_invocation(self):
        """Skill teaches invoking resolution-advisor sub-skill."""
        c = read_report()
        assert "resolution-advisor" in c or "resolution advisor" in c.lower(), (
            "must reference resolution-advisor sub-skill"
        )
