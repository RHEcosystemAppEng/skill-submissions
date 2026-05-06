"""
Tests for rh-virt__vm-rebalance per-skill evaluation.

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

    def test_mentions_migration(self):
        content = read_report().lower()
        assert "migrat" in content, "report should discuss migration"

    def test_report_has_structure(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"


class TestSkillDependent:
    def test_cpu_allocation_field_path(self):
        """Skill teaches per-VM CPU from spec.domain.cpu.sockets (times
        cores times threads). Without skill, agents use nodes_top runtime."""
        c = read_report()
        assert "spec.domain.cpu" in c or "domain.cpu.sockets" in c, (
            "must reference spec.domain.cpu field path for VM CPU allocation"
        )

    def test_kvm_allocatable_field(self):
        """Skill teaches checking status.allocatable for
        devices.kubevirt.io/kvm to confirm node can run VMs.
        status.capacity.cpu/memory is standard K8s — no uplift."""
        c = read_report()
        has_allocatable_kvm = (
            "allocatable" in c.lower() and "devices.kubevirt.io/kvm" in c
        )
        has_kvm_capacity = "devices.kubevirt.io/kvm" in c
        assert has_allocatable_kvm or has_kvm_capacity, (
            "must reference devices.kubevirt.io/kvm in allocatable/capacity"
        )

    def test_kvm_device_label(self):
        """Skill teaches filtering schedulable nodes via
        devices.kubevirt.io/kvm > 0 and kubevirt.io/schedulable=true.
        Without skill, agents don't know the KVM device resource."""
        c = read_report()
        has_kvm = "devices.kubevirt.io/kvm" in c
        has_schedulable = "kubevirt.io/schedulable" in c
        assert has_kvm or has_schedulable, (
            "must reference devices.kubevirt.io/kvm or kubevirt.io/schedulable "
            "for node eligibility filtering"
        )

    def test_vmim_api(self):
        """Skill teaches VirtualMachineInstanceMigration as the CR for live
        migration. Without skill, agents use generic kubectl drain."""
        c = read_report()
        assert "VirtualMachineInstanceMigration" in c, (
            "must reference VirtualMachineInstanceMigration CR for live migration"
        )

    def test_rwo_blocks_live_migration(self):
        """Skill teaches spec.accessModes RWO blocks live migration;
        must use cold migration. Without skill, agents attempt live."""
        c = read_report().lower()
        has_rwo = "rwo" in c or "readwriteonce" in c
        has_cold = any(t in c for t in [
            "cold migrat", "cannot live", "not supported",
        ])
        assert has_rwo and has_cold, (
            "must identify RWO storage as blocking live migration"
        )
