"""
Tests for rh-sre job-template-creator skill evaluation.
Tests check for the specific AAP template creation workflow from SKILL.md.
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

    def test_report_has_content(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"

    def test_mentions_job_template(self):
        content = read_report().lower()
        assert "template" in content, "report should mention job template"


class TestSkillDependent:
    def test_no_create_tool_limitation(self):
        """SKILL: job_templates_create is NOT available. Must use AAP Web UI."""
        c = read_report().lower()
        has_limitation = any(t in c for t in [
            "web ui", "web interface", "manual",
            "not available", "not currently available",
            "no create tool", "read-only", "read only",
        ])
        assert has_limitation, (
            "must acknowledge that template creation requires AAP Web UI "
            "(SKILL: no create MCP tool available)"
        )

    def test_web_ui_steps(self):
        """SKILL: provides step-by-step Web UI instructions for template creation."""
        c = read_report().lower()
        steps = sum(1 for s in [
            "templates", "create", "name", "inventory",
            "project", "playbook", "credentials", "privilege",
            "become", "save",
        ] if s in c)
        assert steps >= 4, (
            f"should provide detailed template configuration steps; found {steps}/10 terms"
        )

    def test_git_flow_for_playbook(self):
        """SKILL Phase 1: prepare playbook in Git project before template creation."""
        c = read_report().lower()
        has_git = any(t in c for t in [
            "git", "commit", "push", "repository", "repo",
            "project sync", "scm", "playbook path",
        ])
        assert has_git, (
            "must address Git/project setup for playbook before template creation "
            "(SKILL Phase 1)"
        )

    def test_required_template_settings(self):
        """SKILL: template needs become_enabled, ask_job_type_on_launch,
        ask_variables_on_launch, ask_limit_on_launch."""
        c = read_report().lower()
        settings = sum(1 for s in [
            "become_enabled", "become", "privilege escalation",
            "ask_job_type", "job type", "ask_variables", "variables on launch",
            "ask_limit", "limit on launch", "ask_inventory",
        ] if s in c)
        assert settings >= 3, (
            f"should specify required template settings "
            f"(become, ask_job_type, ask_variables, ask_limit); found {settings}"
        )

    def test_existing_projects_from_mcp(self):
        """AAP MCP has projects: 'Remediation Playbooks' (6), 'Compliance Checks' (7),
        'Fleet Reporting' (8). Skilled agent queries and references them."""
        c = read_report().lower()
        has_project = any(t in c for t in [
            "remediation playbooks", "project 6", "compliance checks",
            "fleet reporting", "project id 6",
        ])
        assert has_project, (
            "should reference specific AAP projects from MCP "
            "(Remediation Playbooks, Compliance Checks, Fleet Reporting)"
        )

    def test_existing_inventories_from_mcp(self):
        """AAP MCP has inventories: 'Production Systems' (30 hosts),
        'Staging Systems' (15 hosts), 'All Managed Systems' (63 hosts)."""
        c = read_report().lower()
        has_inv = any(t in c for t in [
            "production systems", "staging systems", "all managed",
            "30 host", "15 host", "63 host",
            "inventory 1", "inventory 2", "inventory 3",
        ])
        assert has_inv, (
            "should reference specific AAP inventories from MCP "
            "(Production Systems, Staging Systems, All Managed)"
        )

    def test_remediation_specific_configuration(self):
        """SKILL: template for CVE remediation needs specific settings like
        become for package updates, ask_job_type for dry-run support."""
        c = read_report().lower()
        has_remediation = any(t in c for t in [
            "cve", "remediation", "patch", "security",
            "vulnerability", "package update",
        ])
        has_become_reason = any(t in c for t in [
            "become", "privilege", "sudo", "root",
            "package update", "system change",
        ])
        assert has_remediation and has_become_reason, (
            "should configure template specifically for CVE remediation "
            "(become for package updates)"
        )

    def test_playbook_path_convention(self):
        """SKILL: playbook path follows playbooks/remediation/ convention."""
        c = read_report().lower()
        has_path = any(t in c for t in [
            "playbooks/remediation", "playbook path",
            "remediation-cve", "cve-remediation",
        ])
        assert has_path, (
            "should specify playbook path following remediation convention"
        )
