"""
Tests for rh-virt__vm-rebalance evaluation.

6 pytest (1 padding + 5 skill-specific) targeting KubeVirt rebalance
knowledge: allocated vs runtime capacity, VMIM mechanism, node
eligibility, storage-aware migration paths, and concurrency limits.
"""
import os
import pytest

REPORT = "/solution/report.md"


def read_report():
    if not os.path.exists(REPORT):
        pytest.fail(f"Required file not found: {REPORT}")
    with open(REPORT) as f:
        return f.read()


def test_mentions_migration():
    """Padding: report exists and mentions migration."""
    content = read_report().lower()
    assert len(content) > 200 and "migrat" in content


def test_allocated_cpu_from_domain():
    """Skill teaches computing allocated CPU from VMI spec.domain.cpu
    (sockets x cores x threads), not runtime nodes_top. Without skill,
    agents use nodes_top which hides idle-VM reservations."""
    c = read_report()
    has_domain_cpu = any(t in c for t in [
        "spec.domain.cpu", "domain.cpu", "sockets", "cores",
    ])
    assert has_domain_cpu, (
        "must reference spec.domain.cpu or sockets/cores for allocated "
        "capacity planning"
    )


def test_node_eligibility_labels():
    """Skill teaches filtering hypervisor nodes by kubevirt.io/schedulable
    and devices.kubevirt.io/kvm. Without skill, agents treat all workers
    as migration-eligible."""
    c = read_report()
    has_schedulable = "kubevirt.io/schedulable" in c
    has_kvm = "devices.kubevirt.io/kvm" in c
    assert has_schedulable or has_kvm, (
        "must reference kubevirt.io/schedulable or devices.kubevirt.io/kvm "
        "for hypervisor eligibility"
    )


def test_vmim_mechanism():
    """Skill teaches creating VirtualMachineInstanceMigration CRs for
    live migration. Without skill, agents suggest kubectl drain or
    generic 'move workloads'."""
    c = read_report()
    assert "VirtualMachineInstanceMigration" in c, (
        "must reference VirtualMachineInstanceMigration CR for live migration"
    )


def test_rwo_blocks_live_migration():
    """Skill teaches that RWO PVCs block live migration, requiring cold
    migration path (stop, set affinity, start). Without skill, agents
    assume all VMs can live-migrate."""
    c = read_report().lower()
    has_rwo = "rwo" in c or "readwriteonce" in c
    has_cold = any(t in c for t in [
        "cold migrat", "cannot live", "not support",
        "stop", "offline migrat",
    ])
    assert has_rwo and has_cold, (
        "must explain that RWO blocks live migration and requires cold path"
    )


def test_hyperconverged_concurrency():
    """Skill teaches HyperConverged concurrency defaults:
    parallelMigrationsPerCluster=5, parallelOutboundMigrationsPerNode=2.
    Without skill, agents migrate everything in parallel."""
    c = read_report()
    has_hc = "HyperConverged" in c or "hyperconverged" in c.lower()
    has_parallel = any(t in c for t in [
        "parallelMigration", "parallel migration",
    ])
    has_limits = "5" in c and "2" in c
    assert has_hc or has_parallel or has_limits, (
        "must reference HyperConverged concurrency limits or parallel "
        "migration defaults (5 cluster / 2 per node)"
    )
