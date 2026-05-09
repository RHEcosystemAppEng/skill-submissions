"""
Tests for rh-virt__vm-snapshot-create per-skill evaluation.

Dead-weight baselines and zero-uplift tests removed.
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


class TestSkillDependent:
    def test_snapshot_gvk(self):
        """Skill teaches snapshot.kubevirt.io/v1beta1 as the apiVersion for
        VirtualMachineSnapshot. Without skill, agents guess a wrong GVK."""
        c = read_report()
        assert "snapshot.kubevirt.io/v1beta1" in c, (
            "must reference exact apiVersion snapshot.kubevirt.io/v1beta1"
        )

    def test_status_indications_field(self):
        """Skill teaches that status.indications on the VirtualMachineSnapshot
        contains GuestAgent/Online values that determine consistency level.
        Without skill, agents don't know this field path."""
        c = read_report()
        assert "status.indications" in c, (
            "must reference status.indications field path for consistency"
        )

    def test_agent_connected_condition(self):
        """Skill teaches AgentConnected condition on the VM/VMI as the way
        to verify guest agent presence before snapshot. Without skill,
        agents check vaguely for 'guest agent' without the exact condition."""
        c = read_report()
        assert "AgentConnected" in c, (
            "must reference AgentConnected condition name"
        )

    def test_volume_snapshot_class_gvk(self):
        """Skill teaches VolumeSnapshotClass with snapshot.storage.k8s.io/v1
        as CSI prerequisite. Without skill, agents skip or use wrong GVK."""
        c = read_report()
        assert "VolumeSnapshotClass" in c, (
            "must reference VolumeSnapshotClass prerequisite check"
        )

    def test_hot_plugged_volume_blocker(self):
        """Skill teaches that hot-plugged volumes block snapshot creation
        and must be persisted into spec.template.spec.volumes first.
        Without skill, agents don't know this prerequisite."""
        c = read_report().lower()
        has_hot_plug = any(t in c for t in [
            "hot-plug", "hotplug", "hot plug",
        ])
        assert has_hot_plug, (
            "must check for hot-plugged volumes as snapshot blocker"
        )

    def test_online_crash_consistent_distinction(self):
        """Skill teaches that Online snapshot WITHOUT GuestAgent indication
        is only crash-consistent (no filesystem freeze), while WITH
        GuestAgent it is application-consistent. Without skill, agents
        don't distinguish consistency levels."""
        c = read_report().lower()
        has_crash = "crash" in c and "consistent" in c
        has_app = "application" in c and "consistent" in c
        has_freeze = "freeze" in c or "thaw" in c or "quiesce" in c
        assert has_crash or has_app or has_freeze, (
            "must distinguish crash-consistent vs application-consistent snapshots"
        )

    def test_volume_snapshot_statuses_field(self):
        """Skill teaches saving status.volumeSnapshotStatuses from the VM
        for storage analysis before creating a snapshot. Without skill,
        agents skip pre-snapshot storage validation."""
        c = read_report()
        has_field = "volumeSnapshotStatus" in c
        has_storage_analysis = any(t in c.lower() for t in [
            "storage analysis", "storage validation", "storage class",
            "csi driver",
        ])
        assert has_field or has_storage_analysis, (
            "must reference volumeSnapshotStatuses or perform storage analysis"
        )

    def test_nine_step_storage_analysis(self):
        """Skill teaches a specific 9-step storage analysis workflow before
        creating a snapshot: verify storage class, check CSI driver, etc.
        Without skill, agents don't perform CSI-level validation."""
        c = read_report().lower()
        has_storage_class = "storage class" in c or "storageclass" in c
        has_csi = "csi" in c
        assert has_storage_class and has_csi, (
            "must perform storage analysis covering both storage class and CSI driver"
        )
