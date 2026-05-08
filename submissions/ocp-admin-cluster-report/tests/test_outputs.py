"""
Tests for ocp-admin__cluster-report per-skill evaluation.

Hybrid approach:
  - Exact-field tests: API field paths / GVKs that only SKILL.md teaches
  - Behavioral tests: report structure and classification logic the skill produces
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

    # -- Exact-field tests (API knowledge only SKILL.md teaches) --

    def test_cluster_version_gvk(self):
        """Skill teaches probing OpenShift via resources_get with
        config.openshift.io/v1 ClusterVersion. Without skill, agents
        use generic API discovery or oc version."""
        c = read_report()
        assert "ClusterVersion" in c and "config.openshift.io" in c, (
            "must reference ClusterVersion with config.openshift.io for "
            "OpenShift detection (exact GVK from skill)"
        )

    def test_desired_version_field(self):
        """Skill teaches reading version from .status.desired.version
        on the ClusterVersion resource. Without skill, agents parse
        oc version output or use other sources."""
        c = read_report()
        assert "desired.version" in c or "desired version" in c.lower(), (
            "must reference desired.version path for cluster version extraction"
        )

    def test_403_vs_404_classification(self):
        """Skill teaches a specific classification table:
        403 = OpenShift (unverified, include), 404 = non-OpenShift (exclude).
        Without skill, agents treat all probe errors the same."""
        c = read_report()
        has_403 = "403" in c
        has_404 = "404" in c
        has_unverified = "unverified" in c.lower()
        assert (has_403 and has_404) or (has_403 and has_unverified), (
            "must distinguish 403 (OpenShift unverified) from 404 (non-OpenShift)"
        )

    def test_projects_list_tool(self):
        """Skill teaches using projects_list MCP tool for OpenShift with
        namespaces_list as fallback for non-OpenShift contexts."""
        c = read_report()
        has_projects_tool = "projects_list" in c
        has_namespaces_tool = "namespaces_list" in c
        assert has_projects_tool or has_namespaces_tool, (
            "must reference projects_list or namespaces_list MCP tool names"
        )

    # -- Behavioral tests (report quality the skill produces) --

    def test_non_openshift_exclusion(self):
        """Skill teaches excluding non-OpenShift contexts by default and
        explaining why. Without skill, agents include everything or skip
        without explanation."""
        c = read_report().lower()
        has_exclusion = any(t in c for t in [
            "excluded", "non-openshift", "not openshift",
            "vanilla kubernetes", "not included",
        ])
        assert has_exclusion, (
            "must explicitly identify and exclude non-OpenShift contexts"
        )

    def test_aggregated_totals(self):
        """Skill template includes a cross-cluster comparison table with
        a Total row. Without skill, agents report each cluster separately."""
        c = read_report().lower()
        has_total = "total" in c
        has_agg = any(t in c for t in [
            "total node", "total cpu", "total memory",
            "across cluster", "aggregate", "combined",
        ])
        assert has_total and has_agg, (
            "must include aggregated cross-cluster totals (nodes, CPU, memory)"
        )

    def test_gpu_inventory(self):
        """Skill template includes a GPU column in node resource tables.
        Without skill, agents typically omit GPU information."""
        c = read_report().lower()
        assert "gpu" in c, "must include GPU information in node resources"

    def test_cluster_verification_section(self):
        """Skill workflow starts with a verification step that classifies
        every context before collecting data. Without skill, agents jump
        straight to querying cluster resources."""
        c = read_report().lower()
        has_verify = any(t in c for t in [
            "verification", "discovery result", "cluster discovery",
            "classified", "probe", "openshift cluster",
        ])
        assert has_verify, (
            "must include a cluster verification/discovery section"
        )

    def test_nodes_top_metrics(self):
        """Skill teaches using nodes_top MCP tool for actual CPU and memory
        utilization alongside static capacity from nodes_list. Without
        skill, agents only report allocatable resources or skip metrics."""
        c = read_report()
        has_nodes_top = "nodes_top" in c
        has_utilization = any(t in c.lower() for t in [
            "utilization", "usage %", "cpu usage", "memory usage",
            "actual usage",
        ])
        assert has_nodes_top or has_utilization, (
            "must reference nodes_top or actual resource utilization metrics"
        )
