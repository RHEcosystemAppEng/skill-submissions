"""AAP MCP Validator tests - 6 MCP servers, env vars."""
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
        assert len(read_report()) > 300

class TestSixMCPServers:
    """Must validate all 6 specific AAP MCP server names."""
    def test_job_management(self):
        assert "job-management" in read_report().lower() or "job management" in read_report().lower()
    def test_inventory_management(self):
        assert "inventory-management" in read_report().lower() or "inventory management" in read_report().lower()
    def test_configuration(self):
        assert "configuration" in read_report().lower()
    def test_security_compliance(self):
        assert "security-compliance" in read_report().lower() or "security compliance" in read_report().lower()
    def test_system_monitoring(self):
        assert "system-monitoring" in read_report().lower() or "system monitoring" in read_report().lower()
    def test_user_management(self):
        assert "user-management" in read_report().lower() or "user management" in read_report().lower()

class TestEnvVars:
    """Skill requires checking AAP_MCP_SERVER and AAP_API_TOKEN."""
    def test_env_vars(self):
        c = read_report()
        assert "AAP_MCP_SERVER" in c or "AAP_API_TOKEN" in c or "environment variable" in c.lower()

class TestValidationStructure:
    def test_structured_results(self):
        c = read_report().lower()
        assert ("status" in c or "ok" in c or "pass" in c) and "server" in c
