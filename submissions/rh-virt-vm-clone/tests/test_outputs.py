"""
Tests for rh-virt__vm-clone per-skill evaluation.

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

    def test_mentions_clone(self):
        content = read_report().lower()
        assert "clone" in content, "report should mention cloning"

    def test_report_has_structure(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"


class TestSkillDependent:
    def test_run_strategy_halted(self):
        """Skill teaches setting runStrategy: Halted on the clone so it
        starts in Stopped state. Without skill, agents start it immediately."""
        c = read_report()
        has_halted = "Halted" in c or "runStrategy" in c
        assert has_halted, (
            "must set runStrategy: Halted on clone spec"
        )

    def test_firmware_uuid_regeneration(self):
        """Skill teaches regenerating domain.firmware.uuid and
        domain.firmware.serial in clone spec to avoid identity collision.
        Without skill, agents clone without regenerating firmware IDs."""
        c = read_report()
        has_fw_uuid = "firmware.uuid" in c or "domain.firmware" in c
        has_serial = "firmware.serial" in c or "serial" in c.lower()
        assert has_fw_uuid or has_serial, (
            "must reference domain.firmware.uuid/serial regeneration"
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
