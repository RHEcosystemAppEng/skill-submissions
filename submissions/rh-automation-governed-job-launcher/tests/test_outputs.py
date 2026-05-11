"""Governed job launcher tests - check mode, approval, relaunch, rollback."""
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

class TestCheckMode:
    """Check mode is a core requirement for governed launches."""
    def test_check_mode_execution(self):
        c = read_report().lower()
        assert "check mode" in c or "check" in c or "dry run" in c
    def test_job_type_check(self):
        c = read_report().lower()
        assert "job_type" in c or "check" in c

class TestApprovalGate:
    def test_human_approval(self):
        c = read_report().lower()
        assert "approv" in c or "confirm" in c or "human" in c

class TestJobMonitoring:
    """Skill requires polling jobs_retrieve and host summaries."""
    def test_job_monitoring(self):
        c = read_report().lower()
        assert "monitor" in c or "poll" in c or "status" in c
    def test_per_host_tracking(self):
        c = read_report().lower()
        assert "host" in c and ("summar" in c or "status" in c or "fail" in c)

class TestFailureHandling:
    """Relaunch and rollback are skill-specific features."""
    def test_relaunch_option(self):
        c = read_report().lower()
        assert "relaunch" in c or "retry" in c or "failed hosts" in c
    def test_rollback_option(self):
        c = read_report().lower()
        assert "rollback" in c or "revert" in c

class TestRiskAwareness:
    def test_prior_risk_analysis(self):
        c = read_report().lower()
        assert "risk" in c and ("analysis" in c or "assess" in c or "prior" in c)
