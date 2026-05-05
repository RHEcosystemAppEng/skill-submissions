"""
Tests for rh-sre__remediation per-skill evaluation.
Baseline tests: any reasonable remediation report passes.
Skill-dependent tests: check for mock-data-specific outputs that require
correct MCP tool usage taught by the skill.
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

    def test_mentions_cve(self):
        content = read_report().lower()
        assert "cve" in content, "report should mention CVE"

    def test_report_has_structure(self):
        content = read_report()
        assert len(content) > 150, "report should have substantial content"


class TestSkillDependent:
    def test_specific_cve_ids_from_mock(self):
        """Mock MCP returns 5 CVE IDs. The skill teaches to call get_cves to
        enumerate the full fleet. Check that mock-specific IDs appear."""
        c = read_report()
        cve_ids = [
            "CVE-2024-12345", "CVE-2024-54321", "CVE-2024-98765",
            "CVE-2024-11111", "CVE-2024-22222",
        ]
        found = sum(1 for cve in cve_ids if cve in c)
        assert found >= 3, (
            f"should discover CVEs from mock MCP (found {found}/5). "
            f"Skill teaches to call get_cves for fleet-wide enumeration."
        )

    def test_playbook_content(self):
        """Skill teaches to call create_vulnerability_playbook which returns
        specific YAML with dnf, become: true, security: true, and
        hosts: targeted_systems. A control agent describes playbooks
        conceptually but won't have these exact mock artifacts."""
        c = read_report().lower()
        markers = ["dnf", "become: true", "security: true", "targeted_systems"]
        found = sum(1 for m in markers if m in c)
        assert found >= 2, (
            f"should include actual playbook content from "
            f"create_vulnerability_playbook (found {found}/4 markers: "
            f"dnf, become: true, security: true, targeted_systems)"
        )

    def test_system_environment_counts(self):
        """Mock fleet has 63 systems: 30 prod, 15 staging, 10 dev, 5 QA,
        3 legacy. These exact counts come from calling get_host_details
        and classifying by tags — skill teaches this workflow."""
        c = read_report()
        exact_counts = ["63", "30", "15", "10"]
        found = sum(1 for n in exact_counts if n in c)
        assert found >= 2, (
            f"should report fleet counts from mock data (found {found}/4 "
            f"of: 63 total, 30 prod, 15 staging, 10 dev). "
            f"Skill: get_host_details + tag classification."
        )

    def test_compliance_framework_references(self):
        """Mock CVE data includes pci_impact, soc2_impact, hipaa_impact
        fields. The skill teaches to incorporate compliance context."""
        c = read_report().lower()
        frameworks = ["pci", "soc2", "soc 2", "hipaa"]
        found = sum(1 for f in frameworks if f in c)
        assert found >= 2, (
            f"should reference compliance frameworks from mock data "
            f"(found {found} of: PCI, SOC2, HIPAA). "
            f"Mock CVEs include compliance impact fields."
        )

    def test_non_remediable_cve_identified(self):
        """CVE-2024-22222 in the mock has remediation_available: False.
        The skill teaches the remediatable gate — check this field before
        generating playbooks. The report should flag this."""
        c = read_report().lower()
        has_cve = "cve-2024-22222" in c
        has_no_remediation = any(t in c for t in [
            "no automated", "not remediable", "no remediation",
            "remediation_available: false", "manual",
            "no playbook", "cannot be remediated automatically",
        ])
        assert has_cve or has_no_remediation, (
            "should identify CVE-2024-22222 as not having automated "
            "remediation (remediation_available: False in mock). "
            "Skill: remediatable gate check."
        )
