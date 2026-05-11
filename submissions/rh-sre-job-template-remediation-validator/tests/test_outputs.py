"""
Tests for rh-sre job-template-remediation-validator skill evaluation.
Checks the specific AAP template validation logic from SKILL.md.
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

    def test_report_has_content(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"

    def test_mentions_job_template(self):
        content = read_report().lower()
        assert "template" in content, "report should mention job template"


class TestSkillDependent:
    def test_six_required_checks(self):
        """SKILL defines 6 required checks: inventory, project, playbook,
        credentials, privilege escalation, ask_job_type_on_launch."""
        c = read_report().lower()
        checks = ["inventory", "project", "playbook", "credential",
                   "privilege escalation", "become_enabled",
                   "ask_job_type_on_launch", "job type"]
        found = sum(1 for ch in checks if ch in c)
        assert found >= 4, (
            f"should validate the 6 required template fields from SKILL "
            f"(inventory, project, playbook, credentials, become, ask_job_type); "
            f"found {found}/8 terms"
        )

    def test_become_enabled_check(self):
        """SKILL: become_enabled must be true for remediation (package updates need sudo)."""
        c = read_report().lower()
        assert any(t in c for t in [
            "become_enabled", "privilege escalation", "become",
            "sudo", "root",
        ]), "must check privilege escalation / become_enabled (SKILL required check)"

    def test_ask_job_type_on_launch(self):
        """SKILL: ask_job_type_on_launch required for dry-run (check) vs run mode."""
        c = read_report().lower()
        has_ask = any(t in c for t in [
            "ask_job_type_on_launch", "ask job type",
            "prompt on launch", "job type on launch",
        ])
        has_reason = any(t in c for t in [
            "dry-run", "dry run", "check mode", "job_type",
        ])
        assert has_ask, (
            "must validate ask_job_type_on_launch (SKILL critical required check)"
        )
        assert has_reason, (
            "should explain why ask_job_type_on_launch matters (dry-run vs run)"
        )

    def test_recommended_checks(self):
        """SKILL defines 3 recommended checks: ask_variables, ask_limit, ask_inventory."""
        c = read_report().lower()
        recs = [
            "ask_variables_on_launch", "ask variables",
            "ask_limit_on_launch", "ask limit",
            "ask_inventory_on_launch", "ask inventory",
        ]
        found = sum(1 for r in recs if r in c)
        assert found >= 2, (
            f"should check recommended fields "
            f"(ask_variables/ask_limit/ask_inventory on launch); found {found}/6"
        )

    def test_specific_template_data_from_mcp(self):
        """AAP MCP has templates: 'CVE Remediation - Kernel Update' (ID 10),
        'CVE Remediation - Package Update' (ID 11), 'CVE Remediation - Generic' (ID 12)."""
        c = read_report().lower()
        has_template = any(t in c for t in [
            "kernel update", "package update", "cve remediation",
            "template 10", "template 11", "template 12",
            "id: 10", "id: 11", "id: 12", "id 10", "id 11", "id 12",
        ])
        assert has_template, (
            "should reference specific template names/IDs from AAP MCP data"
        )

    def test_pass_fail_determination(self):
        """SKILL: PASSED / PASSED WITH WARNINGS / FAILED."""
        c = read_report().lower()
        assert any(t in c for t in [
            "passed", "failed", "pass", "fail", "warnings",
        ]), "report must include pass/fail determination"

    def test_project_verification(self):
        """SKILL Phase 4: verify project exists and sync status (successful/failed/pending).
        MCP has project 6='Remediation Playbooks' status=successful."""
        c = read_report().lower()
        has_project = any(t in c for t in [
            "remediation playbooks", "project 6", "project id 6",
            "project status", "project sync", "scm",
        ])
        assert has_project, (
            "should verify project exists and report sync status (SKILL Phase 4)"
        )

    def test_inventory_verification(self):
        """SKILL Phase 4: verify inventory exists. MCP has inventory 1='Production Systems' (30 hosts)."""
        c = read_report().lower()
        has_inv = any(t in c for t in [
            "production systems", "30 host", "inventory 1",
            "inventory id 1", "inventory exists",
        ])
        assert has_inv, (
            "should verify inventory exists and report details (SKILL Phase 4)"
        )

    def test_structured_report_format(self):
        """SKILL defines a specific report format with Required/Recommended/Context tables."""
        c = read_report().lower()
        sections = sum(1 for s in [
            "required check", "recommended check",
            "context verification", "overall result",
            "required", "recommended",
        ] if s in c)
        assert sections >= 2, (
            "report should follow structured format with Required/Recommended sections"
        )
