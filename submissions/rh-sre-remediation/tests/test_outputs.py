"""
Tests for rh-sre__remediation skill evaluation.

Tests check for knowledge from the skill package (SKILL.md + sub-skill
references) that is only available to the treatment agent. The remediation
skill is a meta-orchestrator across 6 specialized skills.
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

    def test_mentions_remediation(self):
        content = read_report().lower()
        assert "remedia" in content, "report should discuss remediation"

    def test_report_has_structure(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"


class TestSkillDependent:

    def test_six_skill_orchestration(self):
        """Skill teaches a 6-skill strict orchestration: cve-impact ->
        cve-validation -> system-context -> playbook-generator ->
        playbook-executor -> remediation-verifier. Without skill, agents
        do ad-hoc steps or skip phases."""
        c = read_report().lower()
        phases = [
            "impact" in c or "cve-impact" in c,
            "validation" in c or "cve-validation" in c,
            "context" in c or "system-context" in c,
            "playbook" in c and "generat" in c,
            "execut" in c,
            "verif" in c,
        ]
        assert sum(phases) >= 5, (
            "must show at least 5 of 6 orchestrated workflow phases"
        )

    def test_skill_tool_invocation(self):
        """Skill teaches invoking sub-skills via the Skill tool, NOT via
        'Task Output'. Using task output causes 'No task found with ID'
        errors. Without skill, agents don't know this anti-pattern."""
        c = read_report()
        has_skill = "Skill" in c and ("tool" in c.lower() or "invok" in c.lower())
        has_anti = "No task found" in c or "Task Output" in c
        assert has_skill or has_anti

    def test_advisory_available_gate(self):
        """Skill teaches advisory_available as the remediatability gate
        (not rules[]). Without skill, agents check rules[] which can be
        empty even when advisory exists."""
        c = read_report()
        assert "advisory_available" in c

    def test_hitl_plan_before_execution(self):
        """Skill requires presenting a remediation plan template from
        references/01-remediation-plan-template.md BEFORE Step 0.
        Without skill, agents jump straight to execution."""
        c = read_report().lower()
        has_plan = any(t in c for t in [
            "remediation plan", "planned task", "proceed with this plan",
        ])
        assert has_plan

    def test_validator_sequencing(self):
        """Skill teaches validators must run one-at-a-time and return
        explicit results (PASSED/FAILED/PARTIAL) before proceeding.
        Without skill, agents run validators in parallel or skip them."""
        c = read_report()
        has_validator = "mcp-lightspeed-validator" in c or "mcp-aap-validator" in c
        has_result = any(t in c for t in ["PASSED", "FAILED", "PARTIAL"])
        assert has_validator and has_result

    def test_two_mcp_servers(self):
        """Skill teaches two separate MCP servers are required:
        lightspeed-mcp for CVE data and aap-mcp for execution.
        Without skill, agents don't distinguish server contexts."""
        c = read_report()
        has_lightspeed = "lightspeed" in c.lower()
        has_aap = "aap" in c.lower()
        assert has_lightspeed and has_aap

    def test_partial_failure_handling(self):
        """Skill teaches partial invocation failure -> warn, don't
        hard-stop. Without skill, agents abort on first error."""
        c = read_report().lower()
        has_warn = any(t in c for t in [
            "warning", "proceed with warning", "partial",
            "despite", "continue anyway",
        ])
        assert has_warn
