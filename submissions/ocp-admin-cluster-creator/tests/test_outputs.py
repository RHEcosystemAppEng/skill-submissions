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
        """Skill teaches set_host_role tool with exact role values 'master'
        and 'worker'. Without skill, agents use 'control-plane' or
        other Kubernetes terminology."""
        c = read_report()
        assert "set_host_role" in c, (
            "must reference set_host_role tool"
        )
        assert '"master"' in c or "'master'" in c or "master" in c.lower(), (
            "must specify 'master' role (not 'control-plane')"
        )

    def test_cluster_status_lifecycle(self):
        """Skill teaches the full status lifecycle: pending → insufficient →
        ready → preparing-for-installation → installing → installed.
        Without skill, agents don't know the progression."""
        c = read_report().lower()
        has_installing = "installing" in c
        has_installed = "installed" in c
        has_progression = has_installing and has_installed
        assert has_progression, (
            "must reference status lifecycle: installing → installed progression"
        )

    def test_iso_generation_workflow(self):
        """Skill teaches cluster_iso_download_url as the tool to generate
        a discovery ISO that hosts must boot from. Without skill, agents
        don't know the Assisted Installer ISO-based discovery workflow."""
        c = read_report()
        has_iso_tool = "cluster_iso_download_url" in c
        has_iso = "discovery iso" in c.lower() or "boot" in c.lower() and "iso" in c.lower()
        assert has_iso_tool or has_iso, (
            "must reference cluster_iso_download_url or discovery ISO boot process"
        )

    def test_install_cluster_tool(self):
        """Skill teaches install_cluster as a separate explicit tool call
        to trigger installation after readiness validation. Without skill,
        agents don't know installation requires an explicit API trigger."""
        c = read_report()
        assert "install_cluster" in c, (
            "must reference install_cluster tool for triggering installation"
        )
