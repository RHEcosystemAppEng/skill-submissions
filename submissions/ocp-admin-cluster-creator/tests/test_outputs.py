"""
Tests for ocp-admin-cluster-creator per-skill evaluation.

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
    def test_create_cluster_mcp_tool(self):
        """Skill teaches the create_cluster MCP tool from the
        openshift-self-managed server. Without skill, agents describe
        manual installer steps or web console."""
        c = read_report()
        assert "create_cluster" in c, (
            "must reference create_cluster MCP tool"
        )

    def test_list_versions_tool(self):
        """Skill teaches using list_versions MCP tool to discover
        available OpenShift versions. Without skill, agents hardcode
        or guess version availability."""
        c = read_report()
        assert "list_versions" in c, (
            "must reference list_versions MCP tool"
        )

    def test_cluster_iso_download_url(self):
        """Skill teaches using cluster_iso_download_url MCP tool to get
        the discovery ISO URL. Without skill, agents describe manual
        ISO download from console."""
        c = read_report()
        assert "cluster_iso_download_url" in c or "iso_download" in c, (
            "must reference cluster_iso_download_url for discovery ISO"
        )

    def test_install_cluster_tool(self):
        """Skill teaches install_cluster MCP tool to trigger installation
        after host discovery. Without skill, agents don't know the
        programmatic trigger mechanism."""
        c = read_report()
        assert "install_cluster" in c, (
            "must reference install_cluster MCP tool"
        )

    def test_cluster_credentials_download(self):
        """Skill teaches cluster_credentials_download_url for obtaining
        kubeconfig and kubeadmin credentials post-install."""
        c = read_report()
        assert "cluster_credentials_download_url" in c or "credentials_download" in c, (
            "must reference cluster_credentials_download_url"
        )
