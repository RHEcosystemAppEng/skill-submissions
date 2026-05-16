"""
Tests for rh-automation-governance-readiness-assessor per-skill evaluation.

Only differentiating tests kept — dead-weight tests where both
control and treatment pass have been removed.
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
    def test_governance_readiness_doc_reference(self):
        """Skill teaches consulting governance-readiness.md before any MCP
        calls. Without skill, agents skip document consultation entirely."""
        c = read_report().lower()
        assert "governance-readiness" in c, (
            "must reference governance-readiness.md document"
        )

    def test_mcp_server_names(self):
        """Skill teaches the exact 6 AAP MCP server names. Without skill,
        agents don't know the canonical server identifiers."""
        c = read_report()
        servers = [
            "aap-mcp-job-management",
            "aap-mcp-inventory-management",
            "aap-mcp-configuration",
            "aap-mcp-security-compliance",
            "aap-mcp-system-monitoring",
            "aap-mcp-user-management",
        ]
        found = sum(1 for s in servers if s in c)
        assert found >= 3, (
            "must reference at least 3 of the 6 AAP MCP server names"
        )

    def test_credentials_list_tool(self):
        """Skill teaches using credentials_list MCP tool from
        aap-mcp-security-compliance for Domain 4 assessment."""
        c = read_report()
        assert "credentials_list" in c or "credential_types_list" in c, (
            "must reference credentials_list or credential_types_list MCP tool"
        )

    def test_seven_domain_framework(self):
        """Skill teaches the 7-domain assessment framework with specific
        domain names. Without skill, agents produce ad-hoc assessments."""
        c = read_report().lower()
        domains = [
            "workflow governance", "notification coverage",
            "access control", "credential security",
            "execution environment", "workload isolation",
            "audit trail",
        ]
        found = sum(1 for d in domains if d in c)
        assert found >= 3, (
            "must reference at least 3 of the 7 governance domains by name"
        )

    def test_cross_domain_correlation(self):
        """Skill teaches cross-domain correlation analysis for compound
        risks (e.g., RBAC GAP + Credentials). Without skill, agents
        assess domains in isolation."""
        c = read_report().lower()
        assert "cross-domain" in c or "compound" in c or "correlation" in c, (
            "must perform cross-domain correlation analysis"
        )

    def test_aap_mcp_validator_prerequisite(self):
        """Skill teaches running aap-mcp-validator as prerequisite before
        assessment. Without skill, agents skip server validation."""
        c = read_report().lower()
        assert "aap-mcp-validator" in c or "validator" in c, (
            "must reference aap-mcp-validator prerequisite"
        )
