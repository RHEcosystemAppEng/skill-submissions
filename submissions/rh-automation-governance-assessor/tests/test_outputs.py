"""Governance assessor tests - 7+1 domains, scoring, remediation."""
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
        assert len(read_report()) > 600

class TestGovernanceDomains:
    """The 7+1 domains are defined in the skill."""
    def test_workflow_governance(self):
        c = read_report().lower()
        assert "workflow" in c and ("governance" in c or "approval" in c)
    def test_notification_coverage(self):
        c = read_report().lower()
        assert "notification" in c
    def test_rbac(self):
        c = read_report().lower()
        assert "rbac" in c or "access control" in c or "role" in c
    def test_credential_security(self):
        c = read_report().lower()
        assert "credential" in c
    def test_execution_environments(self):
        c = read_report().lower()
        assert "execution environment" in c or "ee" in c or "custom ee" in c
    def test_workload_isolation(self):
        c = read_report().lower()
        assert "isolation" in c or "instance group" in c
    def test_audit_trail(self):
        c = read_report().lower()
        assert "audit" in c

class TestScoring:
    def test_has_scores(self):
        c = read_report()
        assert re.search(r'\d+%', c) or re.search(r'\d+/\d+', c), "Must include scores"
    def test_overall_readiness(self):
        c = read_report().lower()
        assert "readiness" in c or "overall" in c or "pass" in c or "fail" in c

class TestRemediation:
    def test_remediation_items(self):
        c = read_report().lower()
        assert "remediat" in c or "fix" in c or "action" in c or "recommend" in c
