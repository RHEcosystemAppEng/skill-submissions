"""
Tests for rh-virt__vm-snapshot-list evaluation.

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
        for VirtualMachineSnapshot resources. An unskilled agent guesses
        wrong GVKs or uses generic kubectl commands."""
        c = read_report()
        assert "snapshot.kubevirt.io" in c, (
            "must reference snapshot.kubevirt.io apiVersion"
        )

    def test_label_selector_for_vm_filter(self):
        """Skill teaches using vm.kubevirt.io/name labelSelector to filter
        snapshots by VM, with fallback to spec.source.name. An unskilled
        agent lists all snapshots without targeted filtering."""
        c = read_report()
        has_label = "vm.kubevirt.io/name" in c
        has_source = "spec.source.name" in c or "spec.source" in c
        assert has_label or has_source, (
            "must use vm.kubevirt.io/name label or spec.source for VM-specific snapshot discovery"
        )

    def test_failed_snapshot_troubleshooting(self):
        """Skill + docs teach that failed snapshots require investigating
        VolumeSnapshot status, VolumeSnapshotClass, or CSI driver issues.
        The mock data includes production-db-snap-failed. An unskilled
        agent just reports 'Failed' without a diagnostic path."""
        c = read_report()
        has_vol_snap = "VolumeSnapshot" in c
        has_csi = "CSI" in c or "csi" in c
        has_storage_class = "StorageClass" in c or "storage class" in c.lower()
        assert has_vol_snap or has_csi or has_storage_class, (
            "must diagnose failed snapshot via VolumeSnapshot/CSI/StorageClass analysis"
        )

    def test_indications_field(self):
        """Skill teaches that status.indications on snapshots reveals
        consistency info (Online, GuestAgent). The mock data returns
        indications in snapshot status. An unskilled agent ignores
        this field or doesn't know its meaning."""
        c = read_report().lower()
        has_indications = "indications" in c
        has_consistency = ("crash" in c and "consistent" in c) or (
            "application" in c and "consistent" in c
        )
        has_guest_agent = "guestagent" in c or "guest agent" in c
        assert has_indications or has_consistency or has_guest_agent, (
            "must reference indications field or consistency levels from snapshot status"
        )
