"""
Tests for rh-virt__vm-create per-skill evaluation.

Exact-field tests: require API field paths and GVKs that only SKILL.md teaches.
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


class TestSkillDependent:
    def test_printable_status_field(self):
        """Skill teaches status.printableStatus as the field to check after
        creation with exact values: Stopped, Running, Provisioning,
        ErrorUnschedulable, ErrorDataVolumeNotReady.
        Without skill, agents use generic status checks."""
        c = read_report()
        has_field = "printableStatus" in c
        has_values = any(v in c for v in [
            "ErrorUnschedulable", "ErrorDataVolumeNotReady", "Provisioning",
        ])
        assert has_field or has_values, (
            "must reference status.printableStatus or its error values"
        )

    def test_default_storage_class_annotation(self):
        """Skill teaches finding default StorageClass via annotation
        storageclass.kubernetes.io/is-default-class.
        Without skill, agents pick storage class by name guess."""
        c = read_report()
        assert "storageclass.kubernetes.io/is-default-class" in c or \
               "is-default-class" in c, (
            "must reference storageclass.kubernetes.io/is-default-class annotation"
        )

    def test_csv_operator_check(self):
        """Skill teaches checking for CSV (ClusterServiceVersion) with
        operators.coreos.com/v1alpha1 in openshift-cnv namespace to verify
        KubeVirt operator health. Without skill, agents skip operator checks."""
        c = read_report()
        has_csv = "ClusterServiceVersion" in c or "CSV" in c
        has_cnv = "openshift-cnv" in c
        assert has_csv or has_cnv, (
            "must check ClusterServiceVersion in openshift-cnv namespace"
        )

    def test_status_conditions_diagnostics(self):
        """Skill teaches inspecting status.conditions on the VM for
        scheduling and readiness diagnostics. Without skill, agents
        only check if the VM exists."""
        c = read_report()
        assert "status.conditions" in c or "conditions" in c.lower(), (
            "must reference status.conditions for VM diagnostics"
        )

    def test_volume_binding_mode(self):
        """Skill teaches checking StorageClass volumeBindingMode
        (Immediate vs WaitForFirstConsumer). Without skill, agents
        don't check binding mode."""
        c = read_report()
        has_binding = "volumeBindingMode" in c or "WaitForFirstConsumer" in c
        assert has_binding, (
            "must reference volumeBindingMode on StorageClass"
        )
