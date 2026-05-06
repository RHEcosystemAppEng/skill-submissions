"""
Tests for rh-virt__vm-rebalance per-skill evaluation.

Skill-specific knowledge tested:
- Capacity percentages use VM allocations vs node capacity, NOT runtime metrics
- RWO PVCs cannot live migrate (cold migration only)
- VirtualMachineInstanceMigration API for live migration
- Overcommit detection when allocated > capacity
- Cold migration procedure: stop, set nodeAffinity, start
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
    def test_allocation_based_metrics(self):
        """Skill: CPU/memory percentages must be based on VM ALLOCATIONS
        (spec.domain.cpu, spec.domain.memory.guest) vs node CAPACITY
        (status.capacity), NOT runtime metrics from nodes_top.
        Without skill, agents use nodes_top actual usage."""
        c = read_report().lower()
        has_allocation = any(t in c for t in [
            "allocat", "reserved", "requested",
            "spec.domain", "vcpu", "vcpus",
            "domain.cpu", "domain.memory",
        ])
        has_capacity = any(t in c for t in [
            "capacity", "allocatable",
            "status.capacity",
        ])
        assert has_allocation or has_capacity, (
            "should calculate utilization from VM allocations vs node capacity "
            "(skill: NOT runtime metrics from nodes_top)"
        )

    def test_not_runtime_metrics_only(self):
        """Skill: Using ONLY nodes_top or runtime metrics is wrong. The plan
        should base decisions on allocated/reserved resources. Without skill,
        agents look at 'nodes_top' and see low utilization on idle VMs."""
        c = read_report().lower()
        uses_allocation = any(t in c for t in [
            "allocat", "reserved", "request", "spec.domain",
            "vcpu", "capacity",
        ])
        only_runtime = (
            "nodes_top" in c
            and "actual" in c
            and not uses_allocation
        )
        assert not only_runtime, (
            "should NOT rely solely on runtime metrics; must use allocated "
            "capacity (skill: idle VMs still reserve resources)"
        )

    def test_rwo_cold_migration_only(self):
        """Skill: VMs with RWO (ReadWriteOnce) PVCs CANNOT live migrate.
        They must use cold migration. Without skill, agents attempt live
        migration regardless of storage access mode."""
        c = read_report().lower()
        has_rwo = any(t in c for t in [
            "rwo", "readwriteonce", "read write once",
        ])
        has_cold = any(t in c for t in [
            "cold migrat", "cold migration", "cannot live",
            "not supported", "stop", "downtime",
        ])
        assert has_rwo and has_cold, (
            "should identify RWO storage as blocking live migration, "
            "requiring cold migration (skill: Validation 3)"
        )

    def test_rwx_live_migration(self):
        """Skill: VMs with RWX storage can use live migration (near-zero
        downtime). The report should distinguish between storage types."""
        c = read_report().lower()
        has_rwx = any(t in c for t in [
            "rwx", "readwritemany", "read write many",
        ])
        has_live = any(t in c for t in [
            "live migrat", "live migration", "zero downtime",
            "near-zero", "<1s",
        ])
        assert has_rwx and has_live, (
            "should identify RWX storage as supporting live migration"
        )

    def test_overcommit_awareness(self):
        """Skill: After rebalancing, if any node exceeds 100% allocated
        capacity, must warn about overcommit. Without skill, agents
        move VMs without checking post-migration capacity."""
        c = read_report().lower()
        assert any(t in c for t in [
            "overcommit", "over-commit", "exceed",
            "exceed 100", ">100", "over 100",
            "capacity", "throttl",
        ]), (
            "should detect and warn about overcommit risk "
            "(skill: Overcommit Detection and Warning)"
        )

    def test_virtualmachineinstancemigration(self):
        """Skill: Live migration uses VirtualMachineInstanceMigration CR,
        not a generic kubectl command."""
        c = read_report().lower()
        assert any(t in c for t in [
            "virtualmachineinstancemigration",
            "vmi migration", "vmim",
            "migration cr", "migration resource",
        ]), (
            "should reference VirtualMachineInstanceMigration API "
            "(skill: KubeVirt migration CR)"
        )

    def test_cold_migration_procedure(self):
        """Skill: Cold migration = stop VM, set nodeAffinity to target,
        start VM. Must re-read VM after stop for fresh resourceVersion.
        Without skill, agents just restart the VM hoping it lands elsewhere."""
        c = read_report().lower()
        has_stop = any(t in c for t in ["stop", "shut down", "shutdown"])
        has_affinity = any(t in c for t in [
            "nodeaffinity", "node affinity", "affinity",
            "nodeselector", "node selector",
        ])
        has_start = any(t in c for t in ["start", "boot"])
        assert has_stop and has_affinity and has_start, (
            "should describe cold migration: stop, set nodeAffinity, start "
            "(skill: REBALANCE_MANUAL cold migration steps)"
        )
