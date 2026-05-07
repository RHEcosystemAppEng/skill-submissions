"""
Tests for rh-sre__fleet-inventory skill evaluation.

Tests check for knowledge from the skill package (SKILL.md + references/)
that is only available to the treatment agent.
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

    def test_mentions_inventory(self):
        content = read_report().lower()
        assert "inventor" in content or "fleet" in content

    def test_report_has_structure(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"


class TestSkillDependent:

    def test_case_sensitive_status_strings(self):
        """Skill teaches exact case-sensitive status strings:
        'Vulnerable', 'Patched', 'Not Affected'. Without skill,
        agents use lowercase or different terminology."""
        c = read_report()
        has_vulnerable = "Vulnerable" in c
        has_patched = "Patched" in c
        has_not_affected = "Not Affected" in c
        assert sum([has_vulnerable, has_patched, has_not_affected]) >= 2

    def test_stale_definition(self):
        """Skill teaches stale = last check-in > 7 days via
        last_seen timestamp. Without skill, agents don't define
        staleness or use different thresholds."""
        c = read_report()
        has_stale = "stale" in c.lower()
        has_last_seen = "last_seen" in c
        assert has_stale and has_last_seen

    def test_remediation_available_flag(self):
        """Skill teaches remediation_available as a per-system-per-CVE
        boolean flag. Without skill, agents check advisory status
        globally."""
        c = read_report()
        assert "remediation_available" in c

    def test_display_name_and_fqdn(self):
        """Skill teaches host identification via display_name and fqdn
        fields (not generic 'hostname'). Without skill, agents use
        hostname or IP only."""
        c = read_report()
        has_display = "display_name" in c
        has_fqdn = "fqdn" in c
        assert has_display and has_fqdn

    def test_get_host_details_tool(self):
        """Skill teaches get_host_details as the MCP tool for host
        information. Without skill, agents may use wrong tools."""
        c = read_report()
        assert "get_host_details" in c

    def test_get_cve_systems_tool(self):
        """Skill teaches get_cve_systems for querying CVE-affected
        systems. Without skill, agents try to filter host lists
        manually."""
        c = read_report()
        assert "get_cve_systems" in c

    def test_lightspeed_mcp_credentials(self):
        """Skill teaches Lightspeed MCP requires LIGHTSPEED_CLIENT_ID
        and LIGHTSPEED_CLIENT_SECRET. Without skill, agents don't
        know the credential pattern."""
        c = read_report()
        has_creds = "LIGHTSPEED_CLIENT" in c or "lightspeed" in c.lower()
        assert has_creds
