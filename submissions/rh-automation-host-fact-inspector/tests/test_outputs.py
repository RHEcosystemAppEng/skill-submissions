"""Host fact inspector tests - system facts, drift, resource checks."""
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

class TestSystemFacts:
    """Host fact inspection requires specific system data points."""
    def test_os_version(self):
        c = read_report().lower()
        assert "os" in c or "operating system" in c or "rhel" in c
    def test_resource_data(self):
        c = read_report().lower()
        has_disk = "disk" in c
        has_memory = "memory" in c or "ram" in c
        assert has_disk or has_memory, "Must check disk or memory resources"

class TestPlatformDrift:
    """Drift detection between hosts is a key differentiator."""
    def test_drift_analysis(self):
        c = read_report().lower()
        assert "drift" in c or "different" in c or "mismatch" in c or "inconsisten" in c
    def test_comparison(self):
        c = read_report().lower()
        assert "compar" in c or "vs" in c or "failed" in c and "healthy" in c

class TestCorrelation:
    def test_failure_correlation(self):
        c = read_report().lower()
        assert "correlat" in c or "cause" in c or "related" in c
    def test_host_specific_vs_job_specific(self):
        c = read_report().lower()
        assert "host" in c and ("specific" in c or "job" in c or "config" in c)
