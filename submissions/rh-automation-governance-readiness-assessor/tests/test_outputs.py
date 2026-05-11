"""Governance readiness assessor tests - scoped domains, scoring."""
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

class TestCredentialSecurity:
    """Credential security assessment is a specific governance domain."""
    def test_credential_domain(self):
        c = read_report().lower()
        assert "credential" in c
    def test_separation_of_duties(self):
        c = read_report().lower()
        assert "separation" in c or "segregat" in c or "least privilege" in c
    def test_credential_types(self):
        c = read_report().lower()
        types = ["machine", "scm", "vault", "cloud"]
        found = sum(1 for t in types if t in c)
        assert found >= 1, "Should mention specific credential types"

class TestRBAC:
    """RBAC assessment checks teams, roles, privilege."""
    def test_rbac_domain(self):
        c = read_report().lower()
        assert "rbac" in c or "role" in c or "access control" in c
    def test_teams_or_roles(self):
        c = read_report().lower()
        assert "team" in c or "role" in c
    def test_least_privilege(self):
        c = read_report().lower()
        assert "privilege" in c or "admin" in c or "permission" in c

class TestReadinessScoring:
    def test_scoring(self):
        c = read_report()
        assert re.search(r'\d+%', c) or "score" in c.lower()
    def test_remediation(self):
        c = read_report().lower()
        assert "remediat" in c or "recommend" in c or "action" in c

class TestAllSixServers:
    def test_mentions_all_servers(self):
        c = read_report().lower()
        assert "6" in c or "all" in c or "six" in c
