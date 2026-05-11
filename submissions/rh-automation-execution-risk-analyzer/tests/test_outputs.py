"""Execution risk analyzer tests - inventory classification, secret scanning, scope."""
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
        assert len(read_report()) > 400

class TestInventoryClassification:
    """Production/staging/dev classification is skill-specific."""
    def test_risk_classification(self):
        c = read_report().lower()
        assert any(level in c for level in ["critical", "high", "medium", "low"])
    def test_production_identified(self):
        c = read_report().lower()
        assert "production" in c or "prod" in c
    def test_inventory_scope(self):
        c = read_report().lower()
        assert "host" in c and ("count" in c or "scope" in c or "target" in c or re.search(r'\d+\s*host', c))

class TestSecretScanning:
    """Scanning extra_vars for secrets is a key differentiator."""
    def test_extra_vars_inspection(self):
        c = read_report().lower()
        assert "extra_var" in c or "variable" in c
    def test_secret_scanning(self):
        c = read_report().lower()
        assert any(term in c for term in ["secret", "password", "token", "key", "credential", "sensitive"])

class TestCheckMode:
    """Recommending check mode / dry run before production execution."""
    def test_check_mode_recommendation(self):
        c = read_report().lower()
        assert "check mode" in c or "dry run" in c or "check" in c
    def test_approval_gate(self):
        c = read_report().lower()
        assert "approv" in c or "confirm" in c or "gate" in c
