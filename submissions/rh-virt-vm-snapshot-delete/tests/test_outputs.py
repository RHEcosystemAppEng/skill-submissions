"""
Tests for rh-virt__vm-snapshot-delete per-skill evaluation.

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

    def test_mentions_snapshot(self):
        content = read_report().lower()
        assert "snapshot" in content

    def test_report_has_structure(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"


class TestSkillDependent:
    def test_snapshot_gvk(self):
        """Skill teaches snapshot.kubevirt.io/v1beta1 as the apiVersion
        for VirtualMachineSnapshot resources."""
        c = read_report()
        assert "snapshot.kubevirt.io/v1beta1" in c, (
            "must reference snapshot.kubevirt.io/v1beta1 GVK"
        )

    def test_restore_in_use_check(self):
        """Skill teaches checking for active VirtualMachineRestore resources
        before deleting a snapshot. Without skill, agents skip this check."""
        c = read_report()
        assert "VirtualMachineRestore" in c, (
            "must check VirtualMachineRestore for in-use snapshots"
        )

    def test_spec_source_name(self):
        """Skill teaches reading spec.source.name to identify the source VM
        of a snapshot. Without skill, agents guess from the snapshot name."""
        c = read_report()
        assert "spec.source.name" in c or "spec.source" in c, (
            "must reference spec.source.name to identify source VM"
        )

    def test_label_selector_for_siblings(self):
        """Skill teaches using vm.kubevirt.io/name labelSelector to find
        sibling snapshots, with fallback to spec.source.name filtering."""
        c = read_report()
        has_label = "vm.kubevirt.io/name" in c
        has_fallback = "spec.source.name" in c
        assert has_label or has_fallback, (
            "must use vm.kubevirt.io/name label or spec.source.name for sibling discovery"
        )

    def test_rbac_check(self):
        """Skill teaches verifying delete permission on
        snapshot.kubevirt.io/virtualmachinesnapshots."""
        c = read_report()
        has_rbac = "virtualmachinesnapshots" in c.lower() or "can-i" in c
        assert has_rbac, (
            "must verify RBAC for deleting virtualmachinesnapshots"
        )
