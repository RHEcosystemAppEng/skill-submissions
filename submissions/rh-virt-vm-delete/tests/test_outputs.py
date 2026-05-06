"""
Tests for rh-virt__vm-delete per-skill evaluation.

Exact-field tests: require API field paths and label keys that only SKILL.md teaches.
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

    def test_mentions_vm(self):
        content = read_report().lower()
        assert any(t in content for t in ["vm", "virtual machine", "virtualmachine"]), (
            "report should reference the target VM"
        )

    def test_report_has_structure(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"


class TestSkillDependent:
    def test_protected_label_exact(self):
        """Skill teaches metadata.labels key 'protected' with value '"true"'
        blocks deletion. Removal command: oc label vm <name> -n <ns> protected-
        Without skill, agents don't know this specific label convention."""
        c = read_report()
        has_protected_label = (
            "protected" in c
            and ('"true"' in c or "'true'" in c or "true" in c.lower())
        )
        has_label_removal = "protected-" in c or "label" in c.lower()
        assert has_protected_label and has_label_removal, (
            "must reference protected label with value 'true' and its removal"
        )

    def test_datavolume_label_selector(self):
        """Skill teaches discovering associated storage via labelSelector
        vm.kubevirt.io/name on DataVolumes (cdi.kubevirt.io/v1beta1).
        Without skill, agents don't know the exact label key."""
        c = read_report()
        assert "vm.kubevirt.io/name" in c or "cdi.kubevirt.io/v1beta1" in c, (
            "must reference vm.kubevirt.io/name label or cdi.kubevirt.io/v1beta1 "
            "DataVolume GVK for storage discovery"
        )

    def test_printable_status_field(self):
        """Skill teaches checking status.printableStatus for Running/Starting/
        Migrating (need stop) vs Stopped/Halted (safe to delete).
        Without skill, agents don't know this exact field path."""
        c = read_report()
        assert "printableStatus" in c or "status.printableStatus" in c, (
            "must reference printableStatus field for VM state check"
        )

    def test_no_force_delete_policy(self):
        """Skill explicitly forbids --force and --grace-period=0.
        Without skill, agents suggest force deletion for stuck VMs."""
        c = read_report().lower()
        has_rejection = any(p in c for p in [
            "do not use --force", "never use --force", "avoid --force",
            "without --force",
        ]) or ("force" in c and any(t in c for t in [
            "never", "do not", "must not", "avoid", "should not",
        ]))
        assert has_rejection, (
            "must actively reject --force and --grace-period=0 deletion"
        )

    def test_resources_delete_gvk(self):
        """Skill teaches using resources_delete with kubevirt.io/v1
        VirtualMachine for the deletion call.
        Without skill, agents use generic kubectl delete."""
        c = read_report()
        assert "kubevirt.io/v1" in c or "resources_delete" in c, (
            "must reference kubevirt.io/v1 GVK or resources_delete for VM deletion"
        )
