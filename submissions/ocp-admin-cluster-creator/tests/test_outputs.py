"""
Tests for ocp-admin cluster-creator skill evaluation.
Tests check for the Assisted Installer workflow from SKILL.md.
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

    def test_report_has_content(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"

    def test_mentions_openshift(self):
        content = read_report().lower()
        assert "openshift" in content, "report should mention OpenShift"


class TestSkillDependent:
    def test_sno_platform_none_requirement(self):
        """SKILL: SNO platform MUST be 'none' (Red Hat API requirement).
        This is a critical, non-obvious constraint."""
        c = read_report().lower()
        has_platform_none = any(t in c for t in [
            'platform.*none', "platform: none", '"none"',
            "platform type.*none", "platform must be none",
            "platform is.*none", "set to none",
        ])
        has_sno = any(t in c for t in ["sno", "single-node", "single node"])
        assert has_sno, "must address Single Node OpenShift (SNO)"
        assert has_platform_none, (
            "must specify SNO platform as 'none' (SKILL critical requirement)"
        )

    def test_assisted_installer_api(self):
        """SKILL: uses Assisted Installer API (/api/assisted-install/v2)."""
        c = read_report().lower()
        has_ai = any(t in c for t in [
            "assisted installer", "assisted-installer",
            "assisted install", "openshift-self-managed",
        ])
        assert has_ai, (
            "must reference Assisted Installer as the provisioning method "
            "(SKILL: MCP-first approach)"
        )

    def test_version_selection_from_mcp(self):
        """MCP list_versions returns 4.16.3, 4.16.2, 4.15.12, 4.15.11, 4.14.18.
        Task specifies 4.15."""
        c = read_report()
        has_version = any(v in c for v in [
            "4.15", "4.16", "4.14",
        ])
        assert has_version, (
            "should reference specific OpenShift versions from Assisted Installer"
        )

    def test_host_discovery_workflow(self):
        """SKILL Step 8: host discovery after ISO boot, then role assignment."""
        c = read_report().lower()
        has_discovery = any(t in c for t in [
            "host discovery", "discover", "boot",
            "iso", "discovery iso",
        ])
        has_role = any(t in c for t in [
            "role assignment", "master", "worker", "control plane",
            "set_host_role",
        ])
        assert has_discovery, "must describe host discovery process (SKILL Step 8)"
        assert has_role, "must describe role assignment (master/worker)"

    def test_iso_generation(self):
        """SKILL Step 7: generate cluster ISO for host boot."""
        c = read_report().lower()
        has_iso = any(t in c for t in [
            "iso", "cluster_iso", "download url",
            "boot media", "discovery image",
        ])
        assert has_iso, (
            "must describe ISO generation for host bootstrapping (SKILL Step 7)"
        )

    def test_vip_configuration_awareness(self):
        """SKILL: HA clusters need API VIP and Ingress VIP. SNO does NOT use VIPs."""
        c = read_report().lower()
        has_vip = any(t in c for t in [
            "vip", "api_vip", "ingress_vip", "virtual ip",
            "api vip", "ingress vip",
        ])
        assert has_vip, (
            "must address VIP configuration (SKILL: required for HA, not for SNO)"
        )

    def test_create_cluster_params(self):
        """SKILL: create_cluster needs name, base_dns_domain, openshift_version,
        high_availability_mode, platform, cpu_architecture."""
        c = read_report().lower()
        params = sum(1 for p in [
            "name", "base_dns_domain", "dns domain", "base domain",
            "openshift_version", "version",
            "high_availability_mode", "availability",
            "platform", "cpu_architecture", "architecture", "x86_64",
        ] if p in c)
        assert params >= 4, (
            f"should specify create_cluster parameters; found {params} relevant terms"
        )

    def test_installation_monitoring(self):
        """SKILL Step 11: monitor installation progress via cluster_info polling."""
        c = read_report().lower()
        has_monitor = any(t in c for t in [
            "monitor", "installation progress", "status",
            "cluster_info", "polling", "installing",
        ])
        assert has_monitor, (
            "must describe installation monitoring (SKILL Step 11)"
        )

    def test_credential_retrieval(self):
        """SKILL Step 12: retrieve kubeconfig after installation."""
        c = read_report().lower()
        has_creds = any(t in c for t in [
            "kubeconfig", "credential", "kubeadmin",
            "credentials_download", "cluster_credentials",
        ])
        assert has_creds, (
            "must describe credential retrieval after installation (SKILL Step 12)"
        )

    def test_mcp_tools_referenced(self):
        """SKILL uses specific MCP tools: list_versions, create_cluster,
        cluster_iso_download_url, install_cluster, etc."""
        c = read_report().lower()
        tools = ["list_versions", "create_cluster", "cluster_iso",
                 "install_cluster", "cluster_info", "set_host_role"]
        found = sum(1 for t in tools if t in c)
        assert found >= 2, (
            f"should reference specific Assisted Installer MCP tools; found {found}/6"
        )
