"""
Tests for rh-virt__vm-snapshot-create evaluation.

6 tests: 2 padding (both agents pass) + 4 skill-dependent.
Each test worth ~16.7% of pytest score.
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

    def test_mentions_production_db(self):
        c = read_report().lower()
        assert "production-db" in c or "production_db" in c, (
            "report must reference the target VM production-db"
        )


class TestSkillDependent:
    def test_snapshot_api_version(self):
        """Skill teaches snapshot.kubevirt.io/v1beta1 as the exact apiVersion
        for VirtualMachineSnapshot. An unskilled agent guesses wrong GVKs
        or uses generic kubectl snapshot commands."""
        c = read_report()
        assert "snapshot.kubevirt.io" in c, (
            "must reference snapshot.kubevirt.io apiVersion"
        )

    def test_agent_connected_condition(self):
        """Skill teaches checking the AgentConnected condition on the VM to
        verify qemu-guest-agent is running BEFORE creating the snapshot.
        An unskilled agent mentions 'guest agent' vaguely without the
        exact condition name."""
        c = read_report()
        assert "AgentConnected" in c, (
            "must reference AgentConnected condition for guest agent verification"
        )

    def test_consistency_distinction(self):
        """Skill teaches that Online snapshot WITHOUT guest agent indication
        is only crash-consistent, while WITH guest agent it achieves
        application-consistent via filesystem freeze/thaw. An unskilled
        agent doesn't distinguish these consistency levels."""
        c = read_report().lower()
        has_crash = "crash" in c and "consistent" in c
        has_app = "application" in c and "consistent" in c
        has_freeze = "freeze" in c or "thaw" in c or "quiesce" in c
        assert has_crash or has_app or has_freeze, (
            "must distinguish crash-consistent vs application-consistent snapshots"
        )

    def test_hot_plugged_volume_blocker(self):
        """Skill teaches that hot-plugged volumes BLOCK snapshot creation
        and must be persisted into spec.template.spec.volumes first.
        An unskilled agent doesn't know this KubeVirt-specific blocker."""
        c = read_report().lower()
        assert any(t in c for t in ["hot-plug", "hotplug", "hot plug"]), (
            "must identify hot-plugged volumes as snapshot creation blocker"
        )
