"""
Tests for rh-virt__vm-snapshot-delete evaluation.

6 tests: 2 padding (both agents pass) + 4 skill-dependent.
Each test worth ~16.7% of pytest score.
"""
import os
import re
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

    def test_mentions_production_db(self):
        c = read_report().lower()
        assert "production-db" in c or "production_db" in c, (
            "report must reference the target VM production-db"
        )


class TestSkillDependent:
    def test_snapshot_api_version(self):
        """Skill teaches snapshot.kubevirt.io/v1beta1 as the apiVersion
        for VirtualMachineSnapshot. An unskilled agent uses generic
        kubectl or wrong GVKs."""
        c = read_report()
        assert "snapshot.kubevirt.io" in c, (
            "must reference snapshot.kubevirt.io apiVersion"
        )

    def test_restore_dependency_check(self):
        """Skill teaches checking for active VirtualMachineRestore resources
        that reference this snapshot BEFORE deletion. The instruction also
        asks for this. An unskilled agent deletes without checking restore
        dependencies."""
        c = read_report()
        assert "VirtualMachineRestore" in c or "Restore" in c, (
            "must check for VirtualMachineRestore dependencies before deletion"
        )

    def test_sibling_snapshot_enumeration(self):
        """Skill teaches listing sibling snapshots for the same VM using
        vm.kubevirt.io/name label or spec.source.name to count remaining
        recovery points. An unskilled agent doesn't enumerate siblings."""
        c = read_report()
        has_label = "vm.kubevirt.io/name" in c
        has_source = "spec.source" in c
        has_sibling = any(t in c.lower() for t in [
            "other snapshot", "sibling", "remaining snapshot",
            "recovery point",
        ])
        assert has_label or has_source or has_sibling, (
            "must discover sibling snapshots via label/spec.source or mention remaining recovery points"
        )

    def test_resources_delete_tool(self):
        """Skill teaches using resources_delete MCP tool with the exact
        snapshot.kubevirt.io/v1beta1 GVK. An unskilled agent uses generic
        delete commands or doesn't specify the tool."""
        c = read_report()
        has_tool = "resources_delete" in c
        has_delete_gvk = (
            "snapshot.kubevirt.io" in c and "delete" in c.lower()
        )
        assert has_tool or has_delete_gvk, (
            "must use resources_delete tool or delete with correct snapshot GVK"
        )
