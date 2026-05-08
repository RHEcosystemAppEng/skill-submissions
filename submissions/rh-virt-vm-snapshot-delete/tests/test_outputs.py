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
        assert "spec.source.name" in c, (
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
        """Skill teaches verifying delete permission on the specific
        snapshot.kubevirt.io resource, not just generic can-i."""
        c = read_report()
        assert "virtualmachinesnapshots" in c.lower(), (
            "must verify RBAC for snapshot.kubevirt.io/virtualmachinesnapshots"
        )

    def test_last_snapshot_warning(self):
        """Skill teaches counting sibling snapshots and warning when this
        is the ONLY snapshot for the VM - after deletion no recovery
        points exist. Without skill, agents delete without considering
        whether other snapshots remain."""
        c = read_report().lower()
        has_last = any(t in c for t in [
            "only snapshot", "last snapshot", "no snapshot",
            "no recovery", "sole snapshot",
        ])
        has_count = any(t in c for t in [
            "count snapshot", "snapshot count", "remaining snapshot",
            "other snapshot",
        ])
        assert has_last or has_count, (
            "must warn about last-snapshot-for-VM scenario"
        )

    def test_resources_delete_tool_usage(self):
        """Skill teaches using resources_delete MCP tool with the exact
        snapshot.kubevirt.io/v1beta1 GVK for deletion. Without skill,
        agents use generic kubectl delete."""
        c = read_report()
        assert "resources_delete" in c, (
            "must use resources_delete MCP tool for snapshot deletion"
        )
