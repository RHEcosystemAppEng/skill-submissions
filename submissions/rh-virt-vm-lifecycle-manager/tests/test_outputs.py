"""
Tests for rh-virt-vm-lifecycle-manager per-skill evaluation.

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
    def test_vm_lifecycle_mcp_tool(self):
        """Skill teaches using vm_lifecycle MCP tool from
        openshift-virtualization server for start/stop/restart.
        Without skill, agents describe oc/virtctl commands."""
        c = read_report()
        assert "vm_lifecycle" in c, (
            "must reference vm_lifecycle MCP tool"
        )

    def test_resources_get_for_vm_status(self):
        """Skill teaches using resources_get with kubevirt.io/v1 apiVersion
        to verify VM status after operations."""
        c = read_report()
        assert "resources_get" in c, (
            "must reference resources_get MCP tool for VM status verification"
        )

    def test_kubevirt_api_version(self):
        """Skill teaches the exact apiVersion kubevirt.io/v1 for
        VirtualMachine CRs. Without skill, agents may omit or
        use wrong version."""
        c = read_report()
        assert "kubevirt.io/v1" in c, (
            "must reference kubevirt.io/v1 apiVersion"
        )

    def test_printable_status_field(self):
        """Skill teaches checking status.printableStatus field for
        VM state verification (Running, Stopped). Without skill,
        agents check generic conditions."""
        c = read_report()
        assert "printableStatus" in c, (
            "must reference status.printableStatus field"
        )

    def test_openshift_virtualization_server(self):
        """Skill teaches using openshift-virtualization MCP server.
        Without skill, agents use generic openshift or kubectl."""
        c = read_report()
        assert "openshift-virtualization" in c, (
            "must reference openshift-virtualization MCP server"
        )
