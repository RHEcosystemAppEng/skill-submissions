"""
Tests for rh-sre__remediation per-skill evaluation.
Baseline tests: report structure.
Skill-dependent tests: conceptual checks (no exact tool/field name matching).
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
    def test_phased_workflow(self):
        """Skill: Orchestrate in order: validate → impact → context → playbook → execute → verify.
        Require at least 4 of the 6 phase concepts AND explicit ordering language."""
        c = read_report().lower()
        phases = ["validat", "impact", "context", "playbook", "execut", "verif"]
        found = sum(1 for p in phases if p in c)
        has_order = any(t in c for t in [
            "step", "phase", "stage", "before", "after",
            "workflow order", "sequence", "in order",
        ])
        assert found >= 4 and has_order, (
            f"should define phased workflow with at least 4 of 6 phases "
            f"(found {found}/6) and ordering language"
        )

    def test_remediatable_gate(self):
        """Skill: Gate on CVE validation — if no automated remediation is available,
        document the decision (manual, risk acceptance, etc.) before proceeding."""
        c = read_report().lower()
        has_gate = any(t in c for t in [
            "gate", "prerequisite", "decision point", "checkpoint",
            "remediation available", "remediation_available",
        ])
        has_remediation_check = any(t in c for t in [
            "no remediation", "not remediatable", "manual",
            "no automated", "advisory", "risk accept",
        ])
        assert has_gate and has_remediation_check, (
            "should gate on remediation availability with fallback handling "
            "(skill: Remediatable Gate)"
        )

    def test_plan_validation_before_execute(self):
        """Skill: Present Remediation Plan (summary, table, checklist) for review before execution."""
        c = read_report().lower()
        has_plan = any(t in c for t in ["plan", "checklist", "summary", "table"])
        has_confirm = any(t in c for t in [
            "confirm", "proceed", "approval", "review", "abort", "sign-off",
        ])
        assert has_plan and has_confirm, (
            "should require plan validation before execution (skill: Remediation Plan)"
        )

    def test_dry_run_recommendation(self):
        """Skill: Recommend dry-run first before actual execution."""
        c = read_report().lower()
        assert any(t in c for t in ["dry-run", "dry run", "check mode", "preview"]), (
            "should recommend dry-run first (skill: before execution)"
        )

    def test_two_checkpoint_structure(self):
        """Skill/docs teach two distinct confirmation checkpoints: an upfront planning
        review (before starting remediation) and a pre-execution review (after playbook
        is ready but before running it). Without docs, agents use a single checkpoint."""
        c = read_report().lower()
        has_upfront = any(t in c for t in [
            "part a", "upfront", "pre-step", "before start",
            "planning checkpoint", "initial review",
            "before step 0", "pre-execution plan",
        ])
        has_pre_exec = any(t in c for t in [
            "part b", "pre-execution", "post-step", "before running",
            "execution review", "after step 4", "before execution",
            "execution checkpoint", "approval gate",
        ])
        assert has_upfront or has_pre_exec, (
            "should describe at least one structured checkpoint "
            "(upfront planning review or pre-execution review)"
        )
