"""
Tests for rh-virt__vm-delete evaluation.

6 pytest (1 padding + 5 skill-specific) targeting KubeVirt deletion
safety gates, storage discovery conventions, and stuck-deletion
diagnosis that only SKILL.md teaches.
"""
import os
import pytest

REPORT = "/solution/report.md"


def read_report():
    if not os.path.exists(REPORT):
        pytest.fail(f"Required file not found: {REPORT}")
    with open(REPORT) as f:
        return f.read()


def test_mentions_vm():
    """Padding: report exists and mentions VM."""
    content = read_report()
    assert len(content) > 200 and "VM" in content.upper()


def test_protected_label_gate():
    """Skill teaches checking metadata.labels.protected == 'true' before
    any deletion and removing it via 'oc label ... protected-'. Without
    skill, agents skip this safety gate."""
    c = read_report().lower()
    has_protected = "protected" in c
    has_removal = any(t in c for t in ["protected-", "label", "remove"])
    assert has_protected and has_removal, (
        "must reference protected label check and removal pattern"
    )


def test_printable_status_check():
    """Skill teaches using status.printableStatus to classify VM state
    (Running/Starting/Migrating = must stop first). Without skill,
    agents check generic phase or skip state verification."""
    c = read_report()
    assert "printableStatus" in c or "printable_status" in c or "printable status" in c.lower(), (
        "must reference printableStatus for VM state classification"
    )


def test_storage_discovery_by_label():
    """Skill teaches discovering DataVolumes/PVCs via label selector
    vm.kubevirt.io/name=<vm> on cdi.kubevirt.io/v1beta1. Without skill,
    agents use generic PVC listing or skip storage discovery."""
    c = read_report()
    has_label = "vm.kubevirt.io/name" in c
    has_cdi = "cdi.kubevirt.io" in c
    assert has_label or has_cdi, (
        "must reference vm.kubevirt.io/name label or cdi.kubevirt.io GVK "
        "for storage discovery"
    )


def test_no_force_delete_policy():
    """Skill explicitly prohibits --force and --grace-period=0 for VM
    deletion. Without skill, agents may suggest force-delete as a
    standard troubleshooting step."""
    c = read_report().lower()
    has_force = "force" in c or "grace-period" in c or "grace_period" in c
    has_no = any(t in c for t in [
        "no force", "no --force", "never force", "avoid force",
        "not force", "without force", "don't force", "do not force",
    ])
    assert has_force and has_no, (
        "must explicitly state no-force-delete policy for VMs"
    )


def test_finalizer_diagnosis():
    """Skill teaches that stuck Terminating VMs should be diagnosed via
    finalizers and resources_create_or_update, not force-deleted.
    Without skill, agents suggest force-delete for stuck resources."""
    c = read_report().lower()
    assert "finalizer" in c or "terminating" in c, (
        "must reference finalizer-based diagnosis for stuck deletions"
    )
