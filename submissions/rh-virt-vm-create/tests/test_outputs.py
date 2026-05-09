"""
Tests for rh-virt__vm-create per-skill evaluation.

Only differentiating tests kept — dead-weight and negative-delta
tests removed to maximize uplift signal.
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

    def test_mentions_vm(self):
        content = read_report().lower()
        assert "vm" in content or "virtual machine" in content

    def test_report_has_structure(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"

    def test_csv_operator_check(self):
        """Both agents typically check KubeVirt operator presence."""
        c = read_report()
        has_csv = "ClusterServiceVersion" in c or "CSV" in c
        has_cnv = "openshift-cnv" in c
        assert has_csv or has_cnv, (
            "must check ClusterServiceVersion in openshift-cnv namespace"
        )


class TestSkillDependent:
    def test_default_storage_class_annotation(self):
        """Skill teaches finding default StorageClass via annotation
        storageclass.kubernetes.io/is-default-class.
        Without skill, agents pick storage class by name guess."""
        c = read_report()
        assert "storageclass.kubernetes.io/is-default-class" in c or \
               "is-default-class" in c, (
            "must reference storageclass.kubernetes.io/is-default-class annotation"
        )

    def test_printable_status_error_values(self):
        """Skill teaches specific printableStatus error values:
        ErrorUnschedulable, ErrorDataVolumeNotReady. Generic 'conditions'
        appears in any K8s output — zero uplift."""
        c = read_report()
        has_errors = any(v in c for v in [
            "ErrorUnschedulable", "ErrorDataVolumeNotReady",
            "DataVolumeReady", "VMIReady",
        ])
        assert has_errors, (
            "must reference specific diagnostic values: ErrorUnschedulable, "
            "ErrorDataVolumeNotReady, DataVolumeReady, or VMIReady"
        )

    def test_resources_create_tool(self):
        """Skill teaches using resources_create_or_update MCP tool to
        create the VM resource. Without skill, agents use kubectl apply."""
        c = read_report()
        assert "resources_create_or_update" in c or "resources_create" in c, (
            "must use resources_create_or_update MCP tool for VM creation"
        )
