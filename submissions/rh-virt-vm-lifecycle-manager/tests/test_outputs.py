"""
Tests for rh-virt__vm-lifecycle-manager evaluation.

6 tests: 2 padding (both agents pass) + 4 skill-dependent.

Skill-dependent tests target knowledge ONLY available through the
SKILL.md and docs/troubleshooting/lifecycle-errors.md — NOT from
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

    def test_mentions_target_vms(self):
        c = read_report().lower()
        has_web = "web-frontend" in c or "web_frontend" in c
        has_db = "production-db" in c or "production_db" in c
        assert has_web or has_db, (
            "report must reference at least one target VM"
        )


class TestSkillDependent:
    def test_stuck_vm_finalizer_diagnosis(self):
        """lifecycle-errors.md teaches checking .metadata.finalizers
        on stuck VMs (kubevirt.io/virtualMachineControllerFinalize,
        foregroundDeletion) as a diagnostic step. This is custom
        troubleshooting doc content unavailable to the control agent."""
        c = read_report().lower()
        has_finalizer = any(t in c for t in [
            "finalizer", "finalizers",
            "virtualMachineControllerFinalize".lower(),
            "foregrounddeletion",
        ])
        has_stuck = any(t in c for t in [
            "stuck", "block", "terminating", "won't stop",
            "not stopping", "unresponsive",
        ])
        assert has_finalizer and has_stuck, (
            "must diagnose stuck VM using finalizer analysis "
            "(lifecycle-errors.md troubleshooting knowledge)"
        )

    def test_vmi_gone_before_start(self):
        """SKILL Step 2 says to verify VMI is NotFound (gone) before
        starting — not just that VM shows Stopped. This is a specific
        verification step from the SKILL workflow."""
        c = read_report().lower()
        has_vmi = "vmi" in c or "virtualmachineinstance" in c
        has_gone = any(t in c for t in [
            "not found", "notfound", "gone", "absent",
            "deleted", "no longer exists",
        ])
        assert has_vmi and has_gone, (
            "must verify VMI is gone (NotFound) before starting, "
            "not just check VM printableStatus (SKILL Step 2)"
        )

    def test_acpi_shutdown_awareness(self):
        """lifecycle-errors.md 'VM Won't Stop' section explains that
        the guest OS may not respond to ACPI shutdown signals and
        provides specific remediation. This is custom doc content."""
        c = read_report().lower()
        has_acpi = "acpi" in c
        has_shutdown = any(t in c for t in [
            "shutdown", "graceful", "signal",
            "guest os", "guest operating system",
        ])
        assert has_acpi and has_shutdown, (
            "must mention ACPI shutdown signal and guest OS response "
            "(lifecycle-errors.md troubleshooting knowledge)"
        )

    def test_error_handling_stop_failure(self):
        """SKILL explicitly states: 'Stop fails during restart → Report,
        do not proceed to start.' This abort-on-failure protocol is
        specific to the SKILL workflow."""
        c = read_report().lower()
        has_stop_fail = any(t in c for t in [
            "stop fails", "stop failure", "fails to stop",
            "stop succeeds but", "if stop",
        ])
        has_abort = any(t in c for t in [
            "do not proceed", "abort", "do not start",
            "remains stopped", "not proceed to start",
            "should not", "must not",
        ])
        assert has_stop_fail and has_abort, (
            "must describe abort-on-failure protocol: if stop fails, "
            "do not proceed to start (SKILL error handling)"
        )
