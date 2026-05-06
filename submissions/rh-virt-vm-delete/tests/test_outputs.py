"""
Tests for rh-virt__vm-delete per-skill evaluation.

Skill-specific knowledge tested:
- protected: "true" label blocks deletion
- Typed VM name confirmation (not yes/no)
- No --force or --grace-period=0 policy
- VM-only vs VM+storage deletion scope
- Stop VM before deletion
- Finalizer handling for stuck Terminating
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
    def test_protected_label_check(self):
        """Skill: VM with label protected='true' MUST NOT be deleted.
        Deletion is refused until label is removed. Without skill,
        agents skip this check and delete regardless."""
        c = read_report().lower()
        has_protected = any(t in c for t in [
            "protected", 'protected: "true"', "protected label",
            "protected: true", "protection label",
        ])
        has_block = any(t in c for t in [
            "refuse", "block", "cannot delete", "must not",
            "prevent", "stop", "remove label", "remove the label",
        ])
        assert has_protected and has_block, (
            "should check for protected:'true' label that blocks deletion "
            "(skill: refuse deletion until label removed)"
        )

    def test_typed_name_confirmation(self):
        """Skill: User must type the exact VM name to confirm deletion
        (case-sensitive). NOT a yes/no prompt. Without skill, agents
        use generic 'Are you sure? yes/no' confirmation."""
        c = read_report().lower()
        has_typed = any(t in c for t in [
            "type the", "type vm", "typed", "exact name",
            "type the name", "type the vm name",
            "case-sensitive", "exact match",
        ])
        assert has_typed, (
            "should require typed VM name confirmation (exact, case-sensitive) "
            "(skill: 'Type <vm> to confirm', not yes/no)"
        )

    def test_no_force_delete(self):
        """Skill: NEVER use --force or --grace-period=0.
        Without skill, agents may suggest force deletion for stuck VMs."""
        c = read_report().lower()
        has_no_force = any(t in c for t in [
            "no force", "never force", "not force",
            "never use --force", "no --force",
            "without force", "avoid force",
        ])
        uses_force = any(t in c for t in [
            "--force", "--grace-period=0",
            "force delete",
        ])
        if uses_force:
            assert has_no_force, (
                "should NOT recommend --force deletion "
                "(skill: 'No Force Delete' policy)"
            )
        else:
            assert True

    def test_storage_scope_distinction(self):
        """Skill: Explicit choice between VM-only (preserve storage) and
        VM+storage (delete DataVolumes and PVCs). Without skill, agents
        delete everything without presenting the choice."""
        c = read_report().lower()
        has_vm_only = any(t in c for t in [
            "vm only", "vm-only", "preserve storage",
            "keep storage", "without storage",
        ])
        has_vm_storage = any(t in c for t in [
            "vm + storage", "vm+storage", "delete storage",
            "including storage", "with storage",
            "datavolume", "pvc",
        ])
        assert has_vm_only or has_vm_storage, (
            "should distinguish VM-only vs VM+storage deletion scope "
            "(skill: explicit storage scope choice)"
        )

    def test_stop_before_delete(self):
        """Skill: Must stop the VM before deletion. Cannot delete a running VM
        safely."""
        c = read_report().lower()
        assert any(t in c for t in [
            "stop", "halt", "shut down", "shutdown",
        ]) and any(t in c for t in [
            "before delet", "before remov", "first",
            "prior to", "must stop",
        ]), (
            "should require stopping VM before deletion"
        )

    def test_finalizer_handling(self):
        """Skill: If VM stuck in Terminating, handle by removing finalizers.
        Without skill, agents just wait or force-delete."""
        c = read_report().lower()
        assert any(t in c for t in [
            "finalizer", "terminating", "stuck",
        ]), (
            "should address finalizer handling for stuck deletion"
        )
