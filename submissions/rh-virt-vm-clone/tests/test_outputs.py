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

    def test_metadata_stripping(self):
        """Skill teaches stripping uid, resourceVersion, creationTimestamp,
        and status from cloned spec. Without skill, agents copy the full
        manifest including server-managed fields."""
        c = read_report()
        strip_fields = sum(1 for f in ["uid", "resourceVersion", "creationTimestamp"]
                          if f in c)
        assert strip_fields >= 2, (
            "must strip uid, resourceVersion, creationTimestamp from clone spec"
        )

    def test_datavolume_label_selector(self):
        """Skill teaches discovering source DataVolumes via labelSelector
        vm.kubevirt.io/name. Without skill, agents manually list volumes."""
        c = read_report()
        assert "vm.kubevirt.io/name" in c, (
            "must use vm.kubevirt.io/name labelSelector for DataVolume discovery"
        )

    def test_datavolume_phase_monitoring(self):
        """Skill teaches monitoring DataVolume status.phase for
        Pending/Succeeded/Failed during clone. Without skill, agents
        don't know the exact status field."""
        c = read_report()
        has_dv_phase = "status.phase" in c
        has_states = any(s in c for s in ["Succeeded", "Pending"])
        assert has_dv_phase or has_states, (
            "must monitor DataVolume status.phase (Pending/Succeeded/Failed)"
        )
