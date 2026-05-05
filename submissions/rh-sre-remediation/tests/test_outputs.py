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

    def test_sub_skill_orchestration(self):
        """Skill teaches: orchestrate specialized sub-skills (cve-validation,
        cve-impact, system-context, playbook-generator, playbook-executor,
        remediation-verifier) rather than doing everything inline."""
        c = read_report().lower()
        sub_skills = [
            "cve-validation", "cve-impact", "system-context",
            "playbook-generator", "playbook-executor", "remediation-verifier",
            "cve_validation", "cve_impact", "system_context",
            "playbook_generator", "playbook_executor", "remediation_verifier",
        ]
        found = sum(1 for s in sub_skills if s in c)
        assert found >= 2, (
            f"should reference specialized sub-skills for orchestration "
            f"(found {found} sub-skill references, need >= 2). "
            f"Skill delegates to: cve-validation, cve-impact, system-context, "
            f"playbook-generator, playbook-executor, remediation-verifier"
        )

    def test_two_checkpoint_structure(self):
        """Skill teaches two distinct confirmation checkpoints:
        Part A (upfront planned-tasks review before Step 0) and
        Part B (execution plan after playbook generation, before execution).
        Without the skill, agents use at most a single generic confirmation."""
        c = read_report().lower()
        has_upfront = any(t in c for t in [
            "part a", "upfront", "planned task",
            "before step 0", "initial review", "planning checkpoint",
            "before any step", "task list",
        ])
        has_pre_exec = any(t in c for t in [
            "part b", "pre-execution", "execution plan",
            "after step 4", "before step 5", "execution review",
            "execution checkpoint", "before execution",
        ])
        assert has_upfront and has_pre_exec, (
            "should describe TWO distinct checkpoints: upfront planning review "
            "(Part A, before starting) AND pre-execution review (Part B, after "
            "playbook ready). Skill teaches this dual-checkpoint pattern."
        )
