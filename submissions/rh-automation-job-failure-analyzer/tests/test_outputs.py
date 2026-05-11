"""Job failure analyzer tests - events, host summaries, error classification."""
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
        assert len(read_report()) > 400

class TestEventExtraction:
    """Job events extraction is the core of failure analysis."""
    def test_events_mentioned(self):
        c = read_report().lower()
        assert "event" in c
    def test_timeline(self):
        c = read_report().lower()
        assert "timeline" in c or "time" in c or "sequence" in c or "order" in c

class TestHostAnalysis:
    def test_host_summaries(self):
        c = read_report().lower()
        assert "host" in c and ("summar" in c or "failed" in c or "success" in c)
    def test_affected_hosts_listed(self):
        c = read_report().lower()
        assert "host" in c and ("error" in c or "fail" in c)

class TestErrorClassification:
    """Error type classification is a specific skill requirement."""
    def test_error_type_classified(self):
        c = read_report().lower()
        error_types = ["connectivity", "privilege", "escalation", "package",
                       "timeout", "syntax", "permission", "unreachable"]
        found = sum(1 for t in error_types if t in c)
        assert found >= 1, "Must classify the error type"
    def test_ansible_task_identified(self):
        c = read_report().lower()
        assert "task" in c or "module" in c or "play" in c

class TestMCPToolUsage:
    def test_job_data(self):
        c = read_report().lower()
        assert "job" in c and ("detail" in c or "status" in c or "retrieve" in c)
    def test_stdout(self):
        c = read_report().lower()
        assert "output" in c or "stdout" in c or "log" in c
