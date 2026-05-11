"""Model monitor skill tests - TrustyAI bias/drift metrics."""
import os, re, pytest

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

class TestTrustyAI:
    """TrustyAI-specific knowledge."""
    def test_trustyai_mentioned(self):
        c = read_report().lower()
        assert "trustyai" in c
    def test_trustyai_service_crd(self):
        c = read_report().lower()
        assert "trustyaiservice" in c or "trustyai service" in c or "crd" in c

class TestBiasMetrics:
    """SPD and DIR are TrustyAI-specific fairness metrics."""
    def test_spd_metric(self):
        c = read_report().lower()
        assert "spd" in c or "statistical parity difference" in c
    def test_dir_metric(self):
        c = read_report().lower()
        assert "dir" in c or "disparate impact ratio" in c
    def test_protected_attribute(self):
        c = read_report().lower()
        assert "protected" in c or "attribute" in c or "applicant" in c
    def test_threshold_values(self):
        c = read_report()
        assert re.search(r'0\.[01]\d*', c), "Must specify numeric threshold"

class TestDriftDetection:
    """Drift detection methods are skill-specific."""
    def test_drift_mentioned(self):
        c = read_report().lower()
        assert "drift" in c
    def test_meanshift_or_fouriermmd(self):
        c = read_report().lower()
        assert "meanshift" in c or "mean shift" in c or "fouriermmd" in c or "fourier" in c or "mmd" in c

class TestPrometheusMetrics:
    """Skill requires querying trustyai_spd/trustyai_dir metrics."""
    def test_prometheus_metrics(self):
        c = read_report().lower()
        assert "trustyai_spd" in c or "trustyai_dir" in c or "prometheus" in c
