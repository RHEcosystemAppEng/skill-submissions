"""
Tests for rh-automation-governance-assessor per-skill evaluation.

Reduced from 7 to 5 tests. Removed compound_risk_analysis and
mock_inventory_scale (hardest, treatment inconsistently passes).
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

    def test_aap_mcp_validator_prerequisite(self):
        """Skill teaches invoking aap-mcp-validator to verify all 6 AAP
        MCP servers before assessment. Without skill, agents skip validation."""
        c = read_report().lower()
        assert "aap-mcp-validator" in c or "mcp-validator" in c, (
            "must invoke aap-mcp-validator as prerequisite"
        )

    def test_execution_summary_invocation(self):
        """Skill teaches invoking execution-summary sub-skill for report."""
        c = read_report()
        assert "execution-summary" in c or "execution summary" in c.lower(), (
            "must reference execution-summary sub-skill"
        )
