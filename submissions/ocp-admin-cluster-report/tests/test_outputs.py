"""
Tests for ocp-admin__cluster-report evaluation.

6 pytest (1 padding + 5 skill-specific) targeting knowledge only
SKILL.md / CLAUDE.md teach — not information visible in raw MCP output.
"""
import os
import pytest

REPORT = "/solution/report.md"


def read_report():
    if not os.path.exists(REPORT):
        pytest.fail(f"Required file not found: {REPORT}")
    with open(REPORT) as f:
        return f.read()


def test_mentions_cluster():
    """Padding: report exists and mentions clusters."""
    content = read_report().lower()
    assert len(content) > 200 and "cluster" in content


def test_cluster_version_gvk():
    """Skill teaches probing OpenShift via resources_get with
    config.openshift.io/v1 ClusterVersion. Without skill, agents
    use generic API discovery or oc version."""
    c = read_report()
    assert "ClusterVersion" in c and "config.openshift.io" in c, (
        "must reference ClusterVersion with config.openshift.io GVK"
    )


def test_403_vs_404_classification():
    """Skill teaches a specific classification table:
    403 = OpenShift (unverified, include), 404 = non-OpenShift (exclude).
    Without skill, agents treat all probe errors the same."""
    c = read_report()
    has_403 = "403" in c
    has_404 = "404" in c
    has_unverified = "unverified" in c.lower()
    assert has_403 and (has_404 or has_unverified), (
        "must distinguish 403 (OpenShift unverified) from 404 (non-OpenShift)"
    )


def test_non_openshift_exclusion():
    """Skill teaches excluding non-OpenShift contexts by default and
    explaining why. Without skill, agents include everything or skip
    without explanation."""
    c = read_report().lower()
    assert any(t in c for t in [
        "excluded", "non-openshift", "not openshift",
        "vanilla kubernetes", "not included",
    ]), "must explicitly identify and exclude non-OpenShift contexts"


def test_aggregation_with_gpu():
    """Skill template includes cross-cluster totals and GPU columns.
    Without skill, agents report per-cluster without aggregation and
    typically omit GPU information."""
    c = read_report().lower()
    has_total = any(t in c for t in [
        "total node", "total cpu", "total memory",
        "across cluster", "aggregate", "combined", "fleet",
    ])
    has_gpu = "gpu" in c
    assert has_total and has_gpu, (
        "must include aggregated cross-cluster totals AND GPU inventory"
    )


def test_nodes_top_utilization():
    """Skill teaches using nodes_top MCP tool for actual CPU and memory
    utilization alongside static capacity. Without skill, agents only
    report allocatable resources."""
    c = read_report()
    has_nodes_top = "nodes_top" in c
    has_utilization = any(t in c.lower() for t in [
        "utilization", "usage %", "cpu usage", "memory usage",
        "actual usage",
    ])
    assert has_nodes_top or has_utilization, (
        "must reference nodes_top or actual resource utilization metrics"
    )
