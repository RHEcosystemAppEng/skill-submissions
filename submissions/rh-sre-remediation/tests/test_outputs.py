"""
Tests for rh-sre__remediation per-skill evaluation.
Baseline tests: any reasonable remediation report passes.
Skill-dependent tests: check for methodology taught by the skill and its references.
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
        assert any(t in content for t in ['remediation', 'orchestrat', 'workflow']), (
            "report should mention key topic"
        )

    def test_report_has_structure(self):
        content = read_report()
        assert len(content) > 150, "report should have substantial content"


class TestSkillDependent:
    def test_mcp_prerequisite_validation(self):
        """Skill teaches: Step 0 — validate MCP server availability (Lightspeed, AAP)
        before any CVE operations. A generic agent won't mention MCP validation."""
        c = read_report().lower()
        has_mcp = any(t in c for t in [
            "mcp", "lightspeed", "aap",
            "prerequisite validation", "server validation",
            "validate prerequisite", "tool validation",
        ])
        has_prereq_step = any(t in c for t in [
            "step 0", "before any", "prerequisite check",
            "validate.*before", "availability check",
        ])
        assert has_mcp or has_prereq_step, (
            "should validate MCP/tool prerequisites before starting "
            "(skill: Step 0 MCP validation)"
        )

    def test_remediatable_gate_with_advisory(self):
        """Skill teaches: gate on remediation availability using Red Hat advisory
        indicators (advisory_available, RHSA, advisories_list). Generic agents
        won't mention advisory-based gating."""
        c = read_report().lower()
        has_advisory_indicator = any(t in c for t in [
            "advisory", "rhsa", "advisories_list", "advisory_available",
            "errata", "security advisory",
        ])
        has_gate = any(t in c for t in [
            "gate", "remediatable", "remediation available",
            "automated remediation", "remediation_available",
        ])
        assert has_advisory_indicator and has_gate, (
            "should gate on remediation availability using Red Hat advisory "
            "indicators (skill: Remediatable Gate with RHSA/advisory check)"
        )

    def test_plan_template_format(self):
        """Skill reference doc teaches a specific plan format: Summary + Table + Checklist.
        Generic agents produce prose, not this structured format."""
        c = read_report().lower()
        has_summary = "summary" in c
        has_table = any(t in c for t in ["table", "| cve", "| target", "| system"])
        has_checklist = any(t in c for t in [
            "checklist", "☐", "☑", "- [", "— done",
            "step 0:", "step 1:", "step 2:",
        ])
        parts_found = sum([has_summary, has_table, has_checklist])
        assert parts_found >= 2, (
            f"should use structured plan format (Summary + Table + Checklist), "
            f"found {parts_found}/3 components (skill: Remediation Plan Template)"
        )

    def test_three_response_options(self):
        """Skill reference 01-remediation-plan-template.md teaches three distinct
        response options at the execution confirmation: proceed/yes, dry-run only,
        and abort. A generic agent will at most offer proceed/abort."""
        c = read_report().lower()
        has_proceed = any(t in c for t in ["proceed", "yes", "confirm"])
        has_dryrun = any(t in c for t in ["dry-run only", "dry run only", "check mode only"])
        has_abort = any(t in c for t in ["abort", "cancel"])
        options_found = sum([has_proceed, has_dryrun, has_abort])
        assert options_found >= 3, (
            f"should offer three response options at execution confirmation: "
            f"proceed, dry-run only, and abort (found {options_found}/3). "
            f"Skill reference: 01-remediation-plan-template.md"
        )

    def test_mcp_tool_awareness(self):
        """Skill teaches specific MCP tool names: get_cve for validation,
        create_vulnerability_playbook for remediation. Generic agents won't
        reference these specific tool names."""
        c = read_report().lower()
        has_tool = any(t in c for t in [
            "get_cve", "create_vulnerability_playbook",
            "vulnerability__get_cve", "vulnerability__explain_cves",
            "explain_cves",
        ])
        assert has_tool, (
            "should reference specific MCP tool names (get_cve, "
            "create_vulnerability_playbook) from the skill's toolset"
        )
