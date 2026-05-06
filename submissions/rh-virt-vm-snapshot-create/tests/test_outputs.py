"""
Tests for rh-virt__vm-snapshot-create per-skill evaluation.

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
        assert "snapshot" in content, "report should mention snapshots"

    def test_report_has_structure(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"


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

    def test_spec_source_shape(self):
        """Skill teaches the snapshot spec.source must include
        apiGroup: kubevirt.io and kind: VirtualMachine. Without skill,
        agents omit or guess apiGroup."""
        c = read_report()
        has_api_group = "apiGroup" in c and "kubevirt.io" in c
        has_source = "spec.source" in c or ("source" in c.lower() and "VirtualMachine" in c)
        assert has_api_group or has_source, (
            "must specify spec.source with apiGroup: kubevirt.io"
        )

    def test_volume_snapshot_class_gvk(self):
        """Skill teaches VolumeSnapshotClass with snapshot.storage.k8s.io/v1
        as CSI prerequisite. Without skill, agents skip or use wrong GVK."""
        c = read_report()
        assert "VolumeSnapshotClass" in c, (
            "must reference VolumeSnapshotClass prerequisite check"
        )
