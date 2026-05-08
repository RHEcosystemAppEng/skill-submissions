"""
Tests for ocp-admin__cluster-inventory per-skill evaluation.

Exact-field tests: require dual-query pattern and field names that only SKILL.md teaches.
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
    def test_dual_mcp_query(self):
        """Skill teaches querying BOTH openshift-self-managed AND
        openshift-ocm-managed MCP servers. Without skill, agents
        query only one and miss half the fleet."""
        c = read_report()
        has_self = "openshift-self-managed" in c or "self-managed" in c
        has_ocm = "openshift-ocm-managed" in c or "ocm-managed" in c
        assert has_self and has_ocm, (
            "must query both openshift-self-managed and openshift-ocm-managed"
        )

    def test_source_field_routing(self):
        """Skill teaches using the cluster's 'source' field to route
        to correct MCP server: 'ocm' -> openshift-ocm-managed,
        'assisted-installer' -> openshift-self-managed.
        Without skill, agents don't know this routing field."""
        c = read_report()
        has_source = "source" in c.lower()
        has_routing = "assisted-installer" in c or "ocm" in c.lower()
        assert has_source and has_routing, (
            "must reference source field for MCP server routing"
        )

    def test_cloud_provider_classification(self):
        """Skill teaches using cloud_provider.id to detect managed flavors:
        aws=ROSA, azure=ARO, gcp=OSD. Without skill, agents don't know
        this classification field."""
        c = read_report()
        has_provider = "cloud_provider" in c
        has_types = sum(1 for t in ["ROSA", "ARO", "OSD"] if t in c)
        assert has_provider or has_types >= 2, (
            "must reference cloud_provider.id for managed cluster classification"
        )

    def test_self_managed_diagnostics(self):
        """Skill teaches that cluster_events and cluster_logs_download_url
        are only available on openshift-self-managed (not ROSA/ARO/OSD).
        Without skill, agents try these tools on all clusters."""
        c = read_report()
        has_events = "cluster_events" in c
        has_logs = "cluster_logs" in c
        assert has_events or has_logs, (
            "must reference cluster_events/cluster_logs for self-managed diagnostics"
        )

    def test_status_filter_vocabulary(self):
        """Skill teaches exact status filter strings including the
        skill-specific 'pending-for-input'. Generic strings like 'ready',
        'error' appear naturally — only pending-for-input discriminates."""
        c = read_report()
        assert "pending-for-input" in c.lower(), (
            "must reference pending-for-input status (skill-specific filter)"
        )
        other_count = sum(1 for s in [
            "ready", "installed", "installing", "error",
        ] if s in c.lower())
        assert other_count >= 2, (
            "must reference at least 2 additional status strings alongside pending-for-input"
        )

    def test_list_clusters_tool(self):
        """Skill teaches using list_clusters MCP tool from both servers
        as the primary discovery mechanism. Without skill, agents use
        kubectl or generic API calls."""
        c = read_report()
        assert "list_clusters" in c, (
            "must use list_clusters MCP tool for cluster discovery"
        )

    def test_cluster_info_tool(self):
        """Skill teaches using cluster_info MCP tool for detail queries,
        routed to the correct server based on source field.
        Without skill, agents don't know this tool exists."""
        c = read_report()
        assert "cluster_info" in c, (
            "must use cluster_info MCP tool for detailed cluster data"
        )

    def test_sno_detection(self):
        """Skill teaches detecting SNO (Single Node OpenShift) via
        platform == none AND single_node == true, distinct from regular
        OCP. Without skill, agents miss SNO classification."""
        c = read_report()
        has_sno = "SNO" in c or "Single Node" in c
        has_single = "single_node" in c.lower()
        assert has_sno or has_single, (
            "must detect and report SNO (Single Node OpenShift) clusters"
        )
