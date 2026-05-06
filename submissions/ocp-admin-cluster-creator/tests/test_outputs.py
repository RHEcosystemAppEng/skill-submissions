"""
Tests for ocp-admin__cluster-creator per-skill evaluation.

Exact-field tests: require API parameter names that only SKILL.md teaches.
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

    def test_mentions_cluster(self):
        content = read_report().lower()
        assert "cluster" in content

    def test_report_has_structure(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"


class TestSkillDependent:
    def test_sno_platform_none(self):
        """Skill teaches that SNO clusters must use platform: 'none'.
        Without skill, agents pick baremetal or vsphere for SNO."""
        c = read_report()
        has_platform = "platform" in c.lower()
        has_none = '"none"' in c or "'none'" in c or "none" in c.lower()
        assert has_platform and has_none, (
            "must set platform to 'none' for SNO cluster"
        )

    def test_create_cluster_tool(self):
        """Skill teaches using create_cluster MCP tool with specific
        parameters: name, version, base_domain, single_node, platform,
        cpu_architecture. Without skill, agents use generic API calls."""
        c = read_report()
        assert "create_cluster" in c, (
            "must reference create_cluster tool"
        )

    def test_set_cluster_vips(self):
        """Skill teaches set_cluster_vips with api_vip and ingress_vip
        for HA clusters (baremetal/vsphere/nutanix only).
        Without skill, agents don't know this separate API call."""
        c = read_report()
        has_vips = "set_cluster_vips" in c
        has_api_vip = "api_vip" in c or "ingress_vip" in c
        assert has_vips or has_api_vip, (
            "must reference set_cluster_vips or api_vip/ingress_vip"
        )

    def test_set_host_role(self):
        """Skill teaches set_host_role with exact role values 'master'
        and 'worker'. Without skill, agents use 'control-plane' or
        other Kubernetes terminology."""
        c = read_report()
        has_tool = "set_host_role" in c
        has_roles = '"master"' in c or '"worker"' in c
        assert has_tool or has_roles, (
            "must reference set_host_role with master/worker roles"
        )

    def test_cluster_status_ready(self):
        """Skill teaches waiting for cluster status 'ready' before
        triggering install, then monitoring for 'installed' or 'error'.
        Without skill, agents don't know the exact status strings."""
        c = read_report()
        has_ready = '"ready"' in c or "'ready'" in c
        has_installed = '"installed"' in c or "'installed'" in c
        assert has_ready or has_installed, (
            "must reference cluster status 'ready' and 'installed'"
        )
