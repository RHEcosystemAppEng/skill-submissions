"""
Tests for rh-virt__vm-snapshot-create evaluation.

6 tests: 2 padding (both agents pass) + 4 skill-dependent.

Skill-dependent tests target knowledge ONLY available through the
SKILL.md and docs/troubleshooting/ — NOT from general KubeVirt
knowledge or mock MCP data exploration.
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
        c = read_report().lower()
        assert "snapshot" in c, "report should mention snapshots"


class TestSkillDependent:
    def test_failed_snapshot_diagnosis(self):
        """Instruction asks to diagnose vm-etl-prod-01-snap-failed.
        The mock MCP shows 'VolumeSnapshot creation timed out' but a
        skilled agent uses storage-errors.md to dig deeper: checking
        CSIDriver capabilities, VolumeSnapshotClass matching, or
        DataVolume/PVC issues — not just echoing the error message."""
        c = read_report().lower()
        has_failed_ref = "etl" in c and ("fail" in c or "timeout" in c)
        has_diagnosis = any(t in c for t in [
            "csidriver", "csi driver",
            "volumesnapshotclass", "volume snapshot class",
            "provisioner", "storage class",
            "timed out",
        ])
        assert has_failed_ref and has_diagnosis, (
            "must diagnose the failed snapshot vm-etl-prod-01-snap-failed "
            "with storage-level root cause analysis"
        )

    def test_volume_snapshot_statuses_on_vm(self):
        """SKILL Step 2 says 'IMPORTANT: Save status.volumeSnapshotStatuses
        for storage analysis.' This field is on the VM resource (not the
        snapshot). The mock MCP does NOT return it, so only a skilled
        agent would know to check/mention it."""
        c = read_report().lower()
        assert "volumesnapshotstatuses" in c, (
            "must reference status.volumeSnapshotStatuses on the VM resource "
            "(SKILL Step 2 prerequisite)"
        )

    def test_resources_create_or_update_tool(self):
        """SKILL Implementation Note: 'This skill uses generic Kubernetes
        resource tools (resources_create_or_update) to manage
        VirtualMachineSnapshot resources. Dedicated snapshot tools do not
        currently exist.' An unskilled agent would not know this."""
        c = read_report().lower()
        assert "resources_create_or_update" in c, (
            "must mention resources_create_or_update as the tool for "
            "creating VirtualMachineSnapshot (SKILL implementation note)"
        )

    def test_csi_driver_snapshot_capability_check(self):
        """SKILL Step 3 mandates verifying CSI driver snapshot
        capabilities as a distinct prerequisite — not just checking
        if a VolumeSnapshotClass exists, but matching the CSI driver
        (provisioner) between StorageClass and VolumeSnapshotClass."""
        c = read_report().lower()
        has_csi = "csi" in c
        has_match = any(t in c for t in [
            "openshift-storage.rbd.csi.ceph.com",
            "provisioner", "driver",
        ])
        has_snapshot_class = any(t in c for t in [
            "volumesnapshotclass", "snapshot class", "snapclass",
        ])
        assert has_csi and has_match and has_snapshot_class, (
            "must verify CSI driver capabilities and match provisioner "
            "between StorageClass and VolumeSnapshotClass (SKILL Step 3)"
        )
