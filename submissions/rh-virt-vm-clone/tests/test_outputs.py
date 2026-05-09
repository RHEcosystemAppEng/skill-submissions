"""
Tests for rh-virt__vm-clone per-skill evaluation.

Only differentiating tests kept — dead-weight tests where both
control and treatment pass 3/3 have been removed.
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
    def test_run_strategy_halted(self):
        """Skill teaches setting runStrategy: Halted on the clone so it
        starts in Stopped state. Without skill, agents start it immediately."""
        c = read_report()
        has_halted = "Halted" in c or "runStrategy" in c
        assert has_halted, (
            "must set runStrategy: Halted on clone spec"
        )

    def test_datavolume_templates_in_clone(self):
        """Skill teaches embedding dataVolumeTemplates in the clone VM spec
        for cross-namespace cloning with independent storage. Without skill,
        agents try to share PVCs across namespaces."""
        c = read_report()
        assert "dataVolumeTemplates" in c or "DataVolumeTemplate" in c, (
            "must reference dataVolumeTemplates for clone storage independence"
        )

    def test_datavolume_label_selector(self):
        """Skill teaches discovering source DataVolumes via labelSelector
        vm.kubevirt.io/name. Without skill, agents manually list volumes."""
        c = read_report()
        assert "vm.kubevirt.io/name" in c, (
            "must use vm.kubevirt.io/name labelSelector for DataVolume discovery"
        )

    def test_cdi_datavolume_gvk(self):
        """Skill teaches DataVolume uses cdi.kubevirt.io/v1beta1 as the
        apiVersion. Without skill, agents use wrong GVK or omit it."""
        c = read_report()
        assert "cdi.kubevirt.io/v1beta1" in c, (
            "must reference cdi.kubevirt.io/v1beta1 for DataVolume GVK"
        )

    def test_metadata_cleanup_on_clone(self):
        """Skill teaches removing uid, resourceVersion, and
        creationTimestamp from cloned VM metadata to avoid conflicts.
        Without skill, agents copy the full spec including server-set
        fields, causing creation errors."""
        c = read_report()
        has_uid = "uid" in c.lower()
        has_rv = "resourceVersion" in c
        has_cleanup = any(t in c.lower() for t in [
            "remove uid", "strip metadata", "clear metadata",
            "remove resourceversion", "server-set",
        ])
        assert has_rv or has_cleanup or has_uid, (
            "must reference removing uid/resourceVersion/creationTimestamp "
            "from cloned metadata"
        )
