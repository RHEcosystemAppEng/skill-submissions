"""
Tests for rh-sre__system-context per-skill evaluation.

Skill-specific knowledge tested:
- infrastructure_type (bare_metal/virtualized/container) and infrastructure_vendor
- needs-restarting command for reboot/service restart assessment
- PDB (PodDisruptionBudget) awareness for Kubernetes safety
- include_system_profile parameter for get_host_details
- Staged rollout by environment/criticality
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

    def test_mentions_topic(self):
        content = read_report().lower()
        assert any(t in content for t in ["system", "context", "fleet"]), (
            "report should mention key topic"
        )

    def test_report_has_structure(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"


class TestSkillDependent:
    def test_infrastructure_type_classification(self):
        """Skill: Systems classified by infrastructure_type field values:
        bare_metal, virtualized, container. Without skill, agents use
        generic terms without the specific field values."""
        c = read_report().lower()
        specific_types = sum(1 for t in [
            "bare_metal", "bare metal",
            "virtualized",
            "container",
        ] if t in c)
        assert specific_types >= 2, (
            "should classify by infrastructure_type: bare_metal, virtualized, "
            "container (skill: specific field values)"
        )

    def test_infrastructure_vendor(self):
        """Skill: infrastructure_vendor field (e.g. kvm, vmware) provides
        additional context about virtualization platform."""
        c = read_report().lower()
        assert any(t in c for t in [
            "infrastructure_vendor", "vendor",
            "kvm", "vmware", "hyper-v",
        ]), (
            "should reference infrastructure_vendor for virtualization platform "
            "(skill: infrastructure_vendor field)"
        )

    def test_needs_restarting(self):
        """Skill: Use 'needs-restarting -r' to check if reboot is required
        after patching (exit 0=no reboot, 1=reboot needed) and '-s' for
        services. Without skill, agents skip this check or guess."""
        c = read_report().lower()
        assert any(t in c for t in [
            "needs-restarting", "needs_restarting",
        ]), (
            "should reference needs-restarting command for reboot/service "
            "restart assessment (skill: specific RHEL utility)"
        )

    def test_pdb_awareness(self):
        """Skill: For Kubernetes nodes, check PodDisruptionBudgets (PDBs)
        before evicting pods during remediation. Without skill, agents
        drain nodes without PDB awareness."""
        c = read_report().lower()
        has_pdb = any(t in c for t in [
            "pdb", "poddisruptionbudget", "pod disruption budget",
            "disruption budget",
        ])
        has_eviction = any(t in c for t in [
            "evict", "eviction", "drain",
        ])
        assert has_pdb and has_eviction, (
            "should check PDBs before pod eviction on Kubernetes nodes "
            "(skill: hasPdbs field, pod eviction safety)"
        )

    def test_staged_rollout_by_environment(self):
        """Skill: Remediate staging first, then production in batches.
        Environment classification drives rollout order."""
        c = read_report().lower()
        has_staging_first = any(t in c for t in [
            "staging first", "test first", "validate first",
            "staging before", "validation phase",
        ])
        has_phases = any(t in c for t in [
            "phase", "batch", "rollout", "rolling",
            "stage 1", "stage 2", "step 1",
        ])
        assert has_staging_first and has_phases, (
            "should recommend staged rollout: staging first, then production "
            "(skill: Decision Matrix)"
        )

    def test_rhel_version_detection(self):
        """Skill: Detect RHEL version distribution across affected systems
        for playbook compatibility (conditional dnf/yum)."""
        c = read_report().lower()
        assert any(t in c for t in [
            "rhel 7", "rhel 8", "rhel 9",
            "rhel7", "rhel8", "rhel9",
            "el7", "el8", "el9",
            "version distribution", "rhel version",
        ]), (
            "should detect RHEL version distribution for playbook compatibility"
        )

    def test_criticality_classification(self):
        """Skill: Systems tagged by criticality (critical/high/medium/low)
        which affects remediation ordering and maintenance windows."""
        c = read_report().lower()
        criticality_terms = sum(1 for t in [
            "critical", "high", "medium", "low",
        ] if t in c)
        has_ordering = any(t in c for t in [
            "priority", "order", "first", "window", "maintenance",
        ])
        assert criticality_terms >= 2 and has_ordering, (
            "should classify by criticality for remediation ordering "
            "(skill: criticality tags)"
        )
