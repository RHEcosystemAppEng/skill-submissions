"""
Tests for rh-virt__vm-snapshot-create per-skill evaluation.

Skill-specific knowledge tested:
- GuestAgent in status.indications = application-consistent; Online without = crash-consistent
- Hot-plugged volumes block snapshot creation entirely
- VolumeSnapshotClass must exist (CSI prerequisite)
- AgentConnected condition on VM for guest agent detection
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
        assert "snapshot" in content, "report should mention snapshots"

    def test_report_has_structure(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"


class TestSkillDependent:
    def test_guest_agent_determines_consistency(self):
        """Skill: If GuestAgent is in status.indications, snapshot is
        application-consistent (filesystem freeze/thaw). If only Online
        without GuestAgent, it's crash-consistent. Without skill, agents
        don't distinguish consistency levels."""
        c = read_report().lower()
        has_guest = any(t in c for t in [
            "guest agent", "guestagent", "qemu-guest-agent",
            "agentconnected",
        ])
        has_consistency = any(t in c for t in [
            "application-consistent", "crash-consistent",
            "quiesce", "freeze", "thaw",
        ])
        assert has_guest and has_consistency, (
            "should explain that GuestAgent presence determines "
            "application-consistent vs crash-consistent snapshot "
            "(skill: status.indications)"
        )

    def test_hot_plug_blocks_snapshot(self):
        """Skill: Hot-plugged volumes (attached without restart) BLOCK
        snapshot creation entirely. Without skill, agents attempt the
        snapshot and fail unexpectedly."""
        c = read_report().lower()
        has_hotplug = any(t in c for t in [
            "hot-plug", "hotplug", "hot plug",
        ])
        has_block = any(t in c for t in [
            "block", "prevent", "cannot", "fail",
            "not possible", "must", "remove",
        ])
        assert has_hotplug and has_block, (
            "should identify hot-plugged volumes as blocking snapshot creation "
            "(skill: volumes attached after VM creation without restart)"
        )

    def test_volume_snapshot_class_prerequisite(self):
        """Skill: VolumeSnapshotClass must exist for the CSI driver before
        any snapshot can be created. Without skill, agents skip this check."""
        c = read_report().lower()
        assert any(t in c for t in [
            "volumesnapshotclass", "volume snapshot class",
            "snapshot class", "csi",
        ]), (
            "should check for VolumeSnapshotClass as CSI prerequisite "
            "(skill: storage prerequisite verification)"
        )

    def test_snapshot_cr_definition(self):
        """Skill: VirtualMachineSnapshot CR with correct apiVersion
        (snapshot.kubevirt.io/v1beta1) and spec.source."""
        c = read_report().lower()
        assert "virtualmachinesnapshot" in c, (
            "should define VirtualMachineSnapshot CR "
            "(skill: snapshot resource specification)"
        )

    def test_online_vs_offline_distinction(self):
        """Skill: Online snapshot (VM running) has different implications
        than offline (VM stopped). Online shows in status.indications."""
        c = read_report().lower()
        has_online = any(t in c for t in [
            "online", "running", "live",
        ])
        has_offline = any(t in c for t in [
            "offline", "stopped", "shut down",
        ])
        has_distinction = any(t in c for t in [
            "status.indications", "indications",
            "consistency", "consistent",
        ])
        assert (has_online or has_offline) and has_distinction, (
            "should distinguish online vs offline snapshot behavior "
            "(skill: status.indications contains 'Online' when running)"
        )

    def test_monitoring_progress(self):
        """Skill: Monitor via status.phase (InProgress/Succeeded/Failed)
        and readyToUse indicator."""
        c = read_report().lower()
        assert any(t in c for t in [
            "readytouse", "ready to use",
            "status.phase", "inprogress", "succeeded",
        ]), (
            "should describe snapshot progress monitoring "
            "(skill: status.phase and readyToUse)"
        )
