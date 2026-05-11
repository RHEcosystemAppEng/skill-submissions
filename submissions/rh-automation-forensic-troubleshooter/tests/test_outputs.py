"""Forensic troubleshooter tests - event extraction, host correlation, resolution."""
import os, pytest

REPORT = "/solution/report.md"

def read_report():
    if not os.path.exists(REPORT):
        pytest.fail(f"Required file not found: {REPORT}")
    with open(REPORT) as f:
        return f.read()

class TestBaseline:
    def test_report_exists(self):
        assert os.path.exists(REPORT)
    def test_report_has_content(self):
        assert len(read_report()) > 500

class TestForensicStructure:
    """Forensic workflow is defined in the skill: events -> host -> classify -> resolve."""
    def test_event_timeline(self):
        c = read_report().lower()
        assert "event" in c and ("timeline" in c or "time" in c or "sequence" in c)
    def test_host_correlation(self):
        c = read_report().lower()
        assert "host" in c and ("correlat" in c or "fact" in c or "failed" in c)
    def test_error_classification(self):
        c = read_report().lower()
        assert "classif" in c or "error type" in c or "category" in c
    def test_root_cause(self):
        c = read_report().lower()
        assert "root cause" in c or "cause" in c

class TestMCPToolUsage:
    """Skill requires specific AAP MCP tools."""
    def test_job_events(self):
        c = read_report().lower()
        assert "event" in c and ("job" in c or "failure" in c)
    def test_host_summaries(self):
        c = read_report().lower()
        assert "host" in c and ("summar" in c or "detail" in c)

class TestResolution:
    def test_resolution_provided(self):
        c = read_report().lower()
        assert "resolution" in c or "recommend" in c or "fix" in c
    def test_red_hat_documentation(self):
        c = read_report().lower()
        assert "red hat" in c or "documentation" in c or "ansible" in c
