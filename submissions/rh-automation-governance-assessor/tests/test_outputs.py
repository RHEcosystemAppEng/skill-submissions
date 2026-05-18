"""
Tests for rh-automation-governance-assessor per-skill evaluation.

Skill orchestrates AAP governance readiness assessment across 7 domains
(Workflow, Notification, RBAC, Credentials, EEs, Isolation, Audit) plus
External Auth bonus. Uses governance-readiness-assessor sub-skill and
consults governance-readiness.md.
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
    def test_governance_domains_coverage(self):
        """Skill teaches 7+1 governance domains. Without skill, agents
        don't know the AAP governance taxonomy."""
        c = read_report().lower()
        domains = [
            "workflow", "notification", "rbac", "credential",
            "execution environment", "instance group", "audit",
        ]
        found = sum(1 for d in domains if d in c)
        assert found >= 4, (
            f"must cover governance domains (workflow, notification, RBAC, "
            f"credentials, EEs, instance groups, audit); found {found}/7"
        )

    def test_governance_readiness_doc(self):
        """Skill teaches consulting governance-readiness.md."""
        c = read_report()
        assert "governance-readiness" in c, (
            "must reference governance-readiness.md"
        )

    def test_compound_risk_analysis(self):
        """Skill teaches cross-domain compound risk analysis — identifying
        risks that emerge from combinations of gaps."""
        c = read_report().lower()
        assert "compound" in c or "cross-domain" in c or "correlation" in c, (
            "must include compound/cross-domain risk analysis"
        )

    def test_aap_mcp_validator_prerequisite(self):
        """Skill teaches invoking aap-mcp-validator to verify all 6 AAP
        MCP servers before assessment. Without skill, agents skip validation."""
        c = read_report().lower()
        assert "aap-mcp-validator" in c or "mcp-validator" in c, (
            "must invoke aap-mcp-validator as prerequisite"
        )

    def test_mock_inventory_scale(self):
        """Mock AAP has 3 inventories: Production (30 hosts), Staging (15),
        All Managed (63). Skilled agent references these to calibrate findings."""
        c = read_report().lower()
        has_data = any(t in c for t in [
            "production systems", "staging systems", "30 host", "15 host",
            "63 host", "all managed",
        ])
        assert has_data, (
            "must reference AAP inventory data from MCP "
            "(Production 30 hosts, Staging 15, All Managed 63)"
        )

    def test_execution_summary_invocation(self):
        """Skill teaches invoking execution-summary sub-skill for report."""
        c = read_report()
        assert "execution-summary" in c or "execution summary" in c.lower(), (
            "must reference execution-summary sub-skill"
        )
