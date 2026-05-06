"""
Tests for rh-sre__fleet-inventory per-skill evaluation.

Exact-field tests: require API field names and status strings that only SKILL.md teaches.
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

    def test_mentions_topic(self):
        content = read_report().lower()
        assert any(t in content for t in ["system", "host", "fleet", "inventory"]), (
            "report should mention key topic"
        )

    def test_report_has_structure(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"


class TestSkillDependent:
    def test_exact_vulnerability_status_strings(self):
        """Skill teaches exact case-sensitive status strings from
        get_cve_systems: 'Vulnerable', 'Patched', 'Not Affected'.
        Without skill, agents use lowercase generic terms."""
        c = read_report()
        exact_count = sum(1 for s in ["Vulnerable", "Patched", "Not Affected"] if s in c)
        assert exact_count >= 2, (
            "must use exact status strings: Vulnerable, Patched, Not Affected "
            "(case-sensitive as returned by API)"
        )

    def test_stale_field(self):
        """Skill teaches the 'stale' boolean field from get_host_details
        and that stale means check-in older than 7 days.
        Without skill, agents don't know this field name."""
        c = read_report()
        has_stale_field = "stale" in c.lower()
        has_last_seen = "last_seen" in c
        assert has_stale_field and has_last_seen, (
            "must reference both stale flag and last_seen field from API"
        )

    def test_remediation_available_flag(self):
        """Skill teaches remediation_available flag on per-system CVE data
        for filtering actionable vulnerabilities.
        Without skill, agents don't know this field exists."""
        c = read_report()
        assert "remediation_available" in c, (
            "must reference remediation_available field for filtering"
        )

    def test_get_cve_systems_tool(self):
        """Skill teaches get_cve_systems with uppercase CVE-YYYY-NNNNN format
        for querying affected systems per CVE.
        Without skill, agents use wrong tool or parameter format."""
        c = read_report()
        has_tool = "get_cve_systems" in c
        has_cve_format = "CVE-" in c
        assert has_tool or has_cve_format, (
            "must reference get_cve_systems tool or CVE-YYYY-NNNNN format"
        )

    def test_display_name_and_fqdn(self):
        """Skill teaches display_name and fqdn as host identification fields
        from get_host_details. Without skill, agents use generic 'hostname'."""
        c = read_report()
        assert "display_name" in c or "fqdn" in c, (
            "must reference display_name or fqdn field from get_host_details"
        )
