"""
Tests for rh-automation-host-fact-inspector per-skill evaluation.

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
    def test_job_troubleshooting_doc(self):
        """Skill teaches consulting job-troubleshooting.md for the
        error-to-fact correlation table. Without skill, agents skip
        document consultation."""
        c = read_report().lower()
        assert "job-troubleshooting" in c, (
            "must reference job-troubleshooting.md document"
        )

    def test_hosts_variable_data_retrieve(self):
        """Skill teaches using hosts_variable_data_retrieve MCP tool to
        get cached Ansible facts. Without skill, agents don't know this
        specific AAP API endpoint."""
        c = read_report()
        assert "hosts_variable_data_retrieve" in c or "variable_data" in c, (
            "must reference hosts_variable_data_retrieve MCP tool"
        )

    def test_ansible_fact_keys(self):
        """Skill teaches specific Ansible fact keys for correlation:
        ansible_mounts, ansible_memtotal_mb, ansible_service_mgr,
        ansible_default_ipv4. Without skill, agents use generic
        system check language."""
        c = read_report()
        facts = [
            "ansible_mounts", "ansible_memtotal_mb",
            "ansible_service_mgr", "ansible_default_ipv4",
            "ansible_python_version",
        ]
        found = sum(1 for f in facts if f in c)
        assert found >= 2, (
            "must reference at least 2 specific Ansible fact keys"
        )

    def test_stale_facts_warning(self):
        """Skill teaches warning about stale cached facts and recommending
        a fresh fact-gathering job. Without skill, agents trust facts
        implicitly."""
        c = read_report().lower()
        assert "stale" in c or "cache" in c or "fact-gathering" in c or (
            "gather" in c and "fact" in c
        ), "must warn about stale facts or recommend fact-gathering job"

    def test_aap_mcp_inventory_management(self):
        """Skill teaches using the aap-mcp-inventory-management server
        for host fact retrieval. Without skill, agents don't know the
        server name."""
        c = read_report()
        assert "aap-mcp-inventory-management" in c or "inventory-management" in c, (
            "must reference aap-mcp-inventory-management server"
        )

    def test_resolution_advisor_next_step(self):
        """Skill teaches routing to resolution-advisor as the next step
        in the forensic pipeline. Without skill, agents don't know
        the skill chain."""
        c = read_report().lower()
        assert "resolution-advisor" in c or "resolution advisor" in c, (
            "must reference resolution-advisor as next step"
        )
