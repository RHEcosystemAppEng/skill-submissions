"""
Tests for rh-basic-red-hat-security-mcp-setup per-skill evaluation.

Only differentiating tests kept — dead-weight tests where both
control and treatment pass 3/3 have been removed.
"""
import os
import pytest

REPORT = "/solution/report.md"


def read_report():
    if not os.path.exists(REPORT):
        pytest.fail(f"Required file not found: {REPORT}")
    with open(REPORT) as f:
        return f.read()


class TestBaseline:
    def test_report_exists(self):
        assert os.path.exists(REPORT), "report.md must exist"


class TestSkillDependent:
    def test_mcp_servers_json_key(self):
        """Skill teaches the exact mcpServers JSON key for .mcp.json
        structure. Without skill, agents use generic config descriptions."""
        c = read_report()
        assert "mcpServers" in c, (
            "must reference mcpServers JSON key"
        )

    def test_http_type_field(self):
        """Skill teaches the exact JSON field 'type': 'http' for HTTP
        transport. Without skill, agents describe transport generically."""
        c = read_report()
        assert '"type"' in c or "'type'" in c, (
            "must show the type field in JSON config"
        )

    def test_cve_explainer_backend_reference(self):
        """Skill teaches that this server is the backend used by
        /red-hat-cve-explainer. Without skill, agents don't know
        the relationship between these skills."""
        c = read_report()
        assert "cve-explainer" in c.lower() or "cve-mcp" in c, (
            "must reference cve-explainer skill or cve-mcp tools"
        )

    def test_exact_server_url(self):
        """Skill teaches the exact URL https://security-mcp.api.redhat.com/mcp
        for the server entry."""
        c = read_report()
        assert "security-mcp.api.redhat.com/mcp" in c, (
            "must include exact server URL"
        )

    def test_no_auth_fields_warning(self):
        """Skill teaches not to add headers or env auth fields —
        the server handles auth via browser SSO."""
        c = read_report().lower()
        has_no_headers = "do not add" in c or "no headers" in c or "not add" in c
        has_sso = "sso" in c or "browser" in c
        assert has_no_headers or has_sso, (
            "must warn about not adding auth fields and explain SSO"
        )
