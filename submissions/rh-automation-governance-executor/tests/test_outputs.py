"""Governance executor tests - risk analysis, check mode, approval, rollback."""
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

class TestGovernedWorkflow:
    """The governed execution workflow has specific phases."""
    def test_risk_analysis_phase(self):
        c = read_report().lower()
        assert "risk" in c and ("analysis" in c or "assess" in c or "classif" in c)
    def test_check_mode(self):
        c = read_report().lower()
        assert "check mode" in c or "dry run" in c
    def test_approval_gate(self):
        c = read_report().lower()
        assert "approv" in c or "confirm" in c or "human" in c
    def test_actual_execution(self):
        c = read_report().lower()
        assert "execut" in c or "launch" in c or "run" in c

class TestRollback:
    def test_rollback_mentioned(self):
        c = read_report().lower()
        assert "rollback" in c or "revert" in c or "undo" in c

class TestMonitoring:
    def test_per_host_status(self):
        c = read_report().lower()
        assert "host" in c and ("status" in c or "progress" in c or "monitor" in c)
