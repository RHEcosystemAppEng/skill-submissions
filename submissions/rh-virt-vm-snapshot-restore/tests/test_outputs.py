"""
Tests for rh-virt__vm-snapshot-restore per-skill evaluation.

Only the 3 strongest differentiating tests kept.
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
    def test_vm_lifecycle_stop_tool(self):
        """Skill teaches using vm_lifecycle MCP tool to stop the VM
        before restore if it's running. Without skill, agents don't know
        the vm_lifecycle tool exists."""
        c = read_report()
        assert "vm_lifecycle" in c, (
            "must use vm_lifecycle MCP tool to stop VM before restore"
        )

    def test_status_restore_time(self):
        """Skill teaches monitoring status.restoreTime on the
        VirtualMachineRestore to capture completion timing. Without
        skill, agents only check status.complete."""
        c = read_report()
        has_restore_time = "restoreTime" in c
        has_timing = any(t in c.lower() for t in [
            "restore time", "completion time", "elapsed",
        ])
        assert has_restore_time or has_timing, (
            "must reference status.restoreTime or capture completion timing"
        )
