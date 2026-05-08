"""
Tests for rh-virt__vm-snapshot-restore per-skill evaluation.

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

    def test_mentions_restore(self):
        content = read_report().lower()
        assert "restore" in content

    def test_report_has_structure(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"


class TestSkillDependent:
    def test_restore_gvk(self):
        """Skill teaches VirtualMachineRestore with apiVersion
        snapshot.kubevirt.io/v1beta1. Without skill, agents don't know
        the correct GVK for restore objects."""
        c = read_report()
        has_restore = "VirtualMachineRestore" in c
        has_gvk = "snapshot.kubevirt.io/v1beta1" in c
        assert has_restore and has_gvk, (
            "must reference VirtualMachineRestore with snapshot.kubevirt.io/v1beta1"
        )

    def test_spec_virtual_machine_snapshot_name(self):
        """Skill teaches spec.virtualMachineSnapshotName as the field
        that links the restore to its source snapshot.
        Without skill, agents use wrong field names."""
        c = read_report()
        assert "virtualMachineSnapshotName" in c, (
            "must reference spec.virtualMachineSnapshotName field"
        )

    def test_spec_target_api_group(self):
        """Skill teaches spec.target with apiGroup: kubevirt.io and
        kind: VirtualMachine. Without skill, agents omit apiGroup."""
        c = read_report()
        assert "spec.target" in c, (
            "must reference spec.target (not bare 'target')"
        )
        assert "apiGroup" in c and "kubevirt.io" in c, (
            "must specify apiGroup: kubevirt.io in spec.target"
        )

    def test_status_complete_field(self):
        """Skill teaches monitoring status.complete (true/false) on the
        VirtualMachineRestore object. Without skill, agents don't know
        the exact monitoring field."""
        c = read_report()
        assert "status.complete" in c, (
            "must monitor status.complete on VirtualMachineRestore"
        )

    def test_snapshot_readiness_check(self):
        """Skill teaches verifying status.readyToUse == true on the
        snapshot before attempting restore."""
        c = read_report()
        assert "readyToUse" in c, (
            "must verify snapshot readyToUse before restore"
        )

    def test_vm_must_be_stopped(self):
        """Skill teaches that VMs MUST be stopped before restore to
        prevent data corruption. The skill provides stop-and-restore vs
        cancel options. Without skill, agents attempt restore on running
        VMs."""
        c = read_report().lower()
        has_stop_req = any(t in c for t in [
            "must be stopped", "stop before", "stop the vm",
            "stop-and-restore", "vm stopped",
        ])
        has_corruption = "corruption" in c or "data loss" in c
        assert has_stop_req or has_corruption, (
            "must require VM to be stopped before restore"
        )

    def test_vm_lifecycle_stop_tool(self):
        """Skill teaches using vm_lifecycle MCP tool to stop the VM
        before restore if it's running. Without skill, agents don't know
        the vm_lifecycle tool exists."""
        c = read_report()
        assert "vm_lifecycle" in c, (
            "must use vm_lifecycle MCP tool to stop VM before restore"
        )

    def test_status_restore_time(self):
        """Skill teaches monitoring status.restoreTime on the
        VirtualMachineRestore to capture completion timing. Without
        skill, agents only check status.complete."""
        c = read_report()
        has_restore_time = "restoreTime" in c
        has_timing = any(t in c.lower() for t in [
            "restore time", "completion time", "elapsed",
        ])
        assert has_restore_time or has_timing, (
            "must reference status.restoreTime or capture completion timing"
        )
