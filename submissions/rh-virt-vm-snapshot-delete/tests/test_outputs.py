"""
Tests for rh-virt__vm-snapshot-delete evaluation.

6 tests: 2 padding (both agents pass) + 4 skill-dependent.

Skill-dependent tests target knowledge ONLY available through the
SKILL.md and docs/troubleshooting/storage-errors.md — NOT from
general KubeVirt knowledge or mock MCP data exploration.
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

    def test_mentions_snapshots(self):
        c = read_report().lower()
        assert "snapshot" in c, "report should mention snapshots"


class TestSkillDependent:
    def test_user_confirmation_requirement(self):
        """SKILL 'Critical: Human-in-the-Loop Requirements' mandates
        'NEVER delete without user confirmation' and 'ALWAYS show what
        will be lost before deletion'. Even in autonomous mode a skilled
        agent documents this protocol. Control agents skip it."""
        c = read_report().lower()
        has_confirm = any(t in c for t in [
            "user confirmation", "confirm", "cannot be undone",
            "yes/no", "proceed with", "approval",
            "human-in-the-loop", "destructive",
        ])
        has_lost = any(t in c for t in [
            "recovery point", "will be lost", "permanently",
            "no undo", "irreversible",
        ])
        assert has_confirm and has_lost, (
            "must describe the confirmation protocol and warn about "
            "permanent data loss (SKILL human-in-the-loop requirement)"
        )

    def test_last_snapshot_warning(self):
        """SKILL Step 4 requires a specific warning when deleting the
        ONLY snapshot for a VM: 'This is the ONLY snapshot for VM...
        After deletion, no snapshot recovery points will exist.'
        Check the report identifies which VMs have only one snapshot."""
        c = read_report().lower()
        has_last = any(t in c for t in [
            "only snapshot", "last snapshot", "no other snapshot",
            "single snapshot", "only recovery point",
            "no snapshot", "no remaining",
        ])
        assert has_last, (
            "must warn when a snapshot is the only/last recovery point "
            "for its VM (SKILL Step 4 last-snapshot warning)"
        )

    def test_storage_cleanup_finalizers(self):
        """storage-errors.md 'Storage Deletion Failures' section teaches
        that PVC/DataVolume may not be freed due to finalizers:
        kubernetes.io/pvc-protection and cdi.kubevirt.io/dataVolumeFinalizer.
        This is custom doc content unavailable to the control agent."""
        c = read_report().lower()
        has_finalizer = any(t in c for t in [
            "finalizer", "pvc-protection",
            "datavolumefinalizer", "datavolumeprotection",
            "cdi.kubevirt.io",
        ])
        has_storage_issue = any(t in c for t in [
            "orphan", "not freed", "still bound", "retain",
            "reclaim policy", "cleanup fail",
        ])
        assert has_finalizer and has_storage_issue, (
            "must diagnose storage cleanup failures via finalizer "
            "analysis (storage-errors.md troubleshooting knowledge)"
        )

    def test_datavolume_before_pvc_ordering(self):
        """storage-errors.md explicitly says: 'Delete DataVolume first,
        then PVC' because DV often blocks PVC deletion. Also mentions
        checking for pods still using the PVC. This is specific
        remediation knowledge from the troubleshooting docs."""
        c = read_report().lower()
        has_dv = any(t in c for t in [
            "datavolume", "data volume",
        ])
        has_ordering = any(t in c for t in [
            "first", "before", "then", "order",
            "sequence", "after",
        ])
        has_pvc = "pvc" in c or "persistentvolumeclaim" in c
        assert has_dv and has_pvc and has_ordering, (
            "must describe DataVolume-before-PVC deletion ordering "
            "(storage-errors.md remediation sequence)"
        )
