"""
Tests for rh-automation-aap-mcp-validator per-skill evaluation.

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
    def test_job_templates_list_tool(self):
        """Skill teaches calling job_templates_list on aap-mcp-job-management
        to validate that server. Without skill, agents do generic health checks."""
        c = read_report()
        assert "job_templates_list" in c, (
            "must reference job_templates_list tool for job-management validation"
        )

    def test_inventories_list_tool(self):
        """Skill teaches calling inventories_list on aap-mcp-inventory-management
        to validate that server."""
        c = read_report()
        assert "inventories_list" in c, (
            "must reference inventories_list tool for inventory-management validation"
        )

    def test_credentials_list_tool(self):
        """Skill teaches calling credentials_list on aap-mcp-security-compliance
        to validate that server."""
        c = read_report()
        assert "credentials_list" in c, (
            "must reference credentials_list tool for security-compliance validation"
        )

    def test_users_list_tool(self):
        """Skill teaches calling users_list on aap-mcp-user-management
        to validate that server."""
        c = read_report()
        assert "users_list" in c, (
            "must reference users_list tool for user-management validation"
        )

    def test_instance_groups_list_tool(self):
        """Skill teaches calling instance_groups_list on
        aap-mcp-system-monitoring to validate that server."""
        c = read_report()
        assert "instance_groups_list" in c, (
            "must reference instance_groups_list tool for system-monitoring validation"
        )
