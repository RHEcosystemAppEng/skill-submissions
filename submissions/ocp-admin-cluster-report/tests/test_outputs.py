"""
Tests for ocp-admin__cluster-report per-skill evaluation.

Exact-field tests: require API field paths and probe logic that only SKILL.md teaches.
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
    def test_cluster_version_probe(self):
        """Skill teaches probing OpenShift via resources_get with
        config.openshift.io/v1 ClusterVersion, name 'version'.
        Without skill, agents use generic API discovery."""
        c = read_report()
        has_cv = "ClusterVersion" in c
        has_api = "config.openshift.io" in c
        assert has_cv or has_api, (
            "must reference ClusterVersion with config.openshift.io for OpenShift detection"
        )

    def test_desired_version_field(self):
        """Skill teaches reading version from .status.desired.version
        on the ClusterVersion resource. Without skill, agents use
        different version sources."""
        c = read_report()
        assert "status.desired.version" in c or "desired.version" in c, (
            "must reference status.desired.version for cluster version"
        )

    def test_403_classification(self):
        """Skill teaches that 403 on ClusterVersion probe means
        'OpenShift (unverified)' — include with version 'unknown'.
        404 means non-OpenShift — exclude. Without skill, agents
        treat all errors the same."""
        c = read_report()
        has_403 = "403" in c
        has_classification = "unverified" in c.lower() or "unknown" in c.lower()
        assert has_403 or has_classification, (
            "must classify 403 as OpenShift (unverified) vs 404 as non-OpenShift"
        )

    def test_projects_list_with_fallback(self):
        """Skill teaches using projects_list for OpenShift, with
        namespaces_list as fallback for vanilla Kubernetes.
        Without skill, agents use only one approach."""
        c = read_report()
        has_projects = "projects_list" in c or "projects" in c.lower()
        has_ns_fallback = "namespaces_list" in c or "namespace" in c.lower()
        assert has_projects and has_ns_fallback, (
            "must use projects_list with namespaces_list fallback"
        )

    def test_artifact_layout(self):
        """Skill teaches specific artifact paths under /tmp/cluster-report/
        and a manifest JSON with $file references.
        Without skill, agents use ad-hoc output paths."""
        c = read_report()
        has_path = "/tmp/cluster-report" in c or "cluster-report" in c
        assert has_path, (
            "must reference /tmp/cluster-report artifact path"
        )
