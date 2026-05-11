"""Red Hat Security MCP Setup tests."""
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
        assert len(read_report()) > 200

class TestMCPServerConfig:
    """Specific MCP server URL and key name from the SKILL.md."""
    def test_server_key_name(self):
        c = read_report()
        assert "red-hat-security" in c
    def test_http_transport(self):
        c = read_report().lower()
        assert "http" in c
    def test_server_url(self):
        c = read_report()
        assert "security-mcp.api.redhat.com" in c or "security-mcp" in c
    def test_mcp_json_file(self):
        c = read_report()
        assert ".mcp.json" in c

class TestMergeNotOverwrite:
    """Skill specifically says merge, not overwrite."""
    def test_merge_behavior(self):
        c = read_report().lower()
        assert "merge" in c or "without removing" in c or "existing" in c

class TestSSOAuth:
    """SSO browser login flow is skill-specific knowledge."""
    def test_sso_mentioned(self):
        c = read_report().lower()
        assert "sso" in c or "browser" in c or "login" in c
    def test_no_headers_or_env(self):
        c = read_report().lower()
        has_warning = "do not add" in c or "no headers" in c or "not add" in c or \
                      "handles authentication" in c or "automatically" in c
        assert has_warning, "Must warn not to add headers/env auth fields"

class TestRedHatAccount:
    """Requires Red Hat account/subscription."""
    def test_red_hat_account(self):
        c = read_report().lower()
        assert "red hat" in c and ("account" in c or "subscription" in c or "console.redhat.com" in c)
