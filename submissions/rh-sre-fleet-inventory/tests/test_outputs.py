"""
Tests for rh-sre-fleet-inventory per-skill evaluation.

Skill teaches querying Red Hat Lightspeed for managed system inventory.
Mock fleet: 63 systems (30 production, 15 staging, 10 dev, 5 QA, 3 legacy).
5 CVEs including CVE-2024-12345 (Critical 9.8) and CVE-2024-54321 (Important 7.5).
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
    def test_get_host_details_tool(self):
        """Skill teaches using get_host_details MCP tool to retrieve
        system inventory. Without skill, agents describe generic commands."""
        c = read_report()
        assert "get_host_details" in c or "get_cve_systems" in c, (
            "must reference get_host_details or get_cve_systems MCP tools"
        )

    def test_mcp_lightspeed_validator_prereq(self):
        """Skill teaches invoking mcp-lightspeed-validator before any
        operations. Without skill, agents skip MCP validation."""
        c = read_report().lower()
        assert "lightspeed-validator" in c or "mcp-lightspeed" in c or (
            "validator" in c and "lightspeed" in c
        ), "must reference mcp-lightspeed-validator as prerequisite"

    def test_mock_fleet_size(self):
        """Mock has 63 total systems (30 production, 15 staging). Skilled
        agent discovers these counts from MCP data."""
        c = read_report()
        assert "63" in c or ("30" in c and "production" in c.lower()), (
            "must report fleet size from MCP data (63 total, 30 production)"
        )

    def test_mock_cve_data(self):
        """Mock has CVE-2024-12345 (Critical 9.8 RCE) and CVE-2024-54321
        (Important 7.5 SQL injection). Skilled agent surfaces these."""
        c = read_report()
        assert "CVE-2024-12345" in c or "CVE-2024-54321" in c, (
            "must reference specific CVEs from mock MCP data"
        )

    def test_environment_breakdown(self):
        """Mock fleet has production, staging, development, QA, and legacy
        environments. Skilled agent breaks down by environment."""
        c = read_report().lower()
        envs = ["production", "staging", "development", "legacy"]
        found = sum(1 for e in envs if e in c)
        assert found >= 3, (
            f"must break down fleet by environment; found {found}/4"
        )

    def test_remediation_transition(self):
        """Skill teaches offering transition to /remediation skill for
        CVE remediation after discovery."""
        c = read_report().lower()
        assert "remediat" in c and ("next step" in c or "transition" in c or "skill" in c), (
            "must offer transition to remediation workflow"
        )
