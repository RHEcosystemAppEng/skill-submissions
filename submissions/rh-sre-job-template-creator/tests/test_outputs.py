"""
Tests for rh-sre__job-template-creator per-skill evaluation.

Skill-specific knowledge tested:
- AAP MCP has NO job_templates_create tool; creation is Web UI only
- Playbook must be committed to Git and project synced before template creation
- become_enabled required for remediation templates
- Prompt on Launch for job type, variables, limit
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
        assert any(t in content for t in ["job template", "template", "ansible"]), (
            "report should mention key topic"
        )

    def test_report_has_structure(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"


class TestSkillDependent:
    def test_web_ui_creation_required(self):
        """Skill: AAP MCP has NO job_templates_create tool. Template creation
        MUST be done via the AAP Web UI. Without skill, agents attempt to
        create templates programmatically via API/MCP."""
        c = read_report().lower()
        has_web_ui = any(t in c for t in [
            "web ui", "web interface", "ui", "manual",
            "browser", "gui", "dashboard",
        ])
        has_no_api = any(t in c for t in [
            "no create", "not available", "cannot create",
            "no api", "read-only", "read only",
            "not currently available", "does not exist",
            "no tool", "not supported",
        ])
        assert has_web_ui or has_no_api, (
            "should state that template creation requires AAP Web UI "
            "(skill: 'job_templates_create NOT CURRENTLY AVAILABLE')"
        )

    def test_no_programmatic_creation_attempt(self):
        """Skill: The agent should NOT suggest calling job_templates_create
        or any API endpoint to create the template. Without skill, agents
        assume a create API exists."""
        c = read_report().lower()
        creates_via_api = any(t in c for t in [
            "job_templates_create(",
            "post /api",
            "api call to create",
            "create endpoint",
        ])
        assert not creates_via_api, (
            "should NOT attempt to create templates via API/MCP "
            "(skill: create tools do not exist)"
        )

    def test_git_before_template(self):
        """Skill: Playbook must be committed to Git and AAP project synced
        BEFORE the template can reference it. Without skill, agents skip
        the Git prerequisite."""
        c = read_report().lower()
        has_git = any(t in c for t in [
            "git", "commit", "push", "repository",
        ])
        has_sync = any(t in c for t in [
            "sync", "project sync", "scm", "update project",
        ])
        assert has_git and has_sync, (
            "should require playbook in Git + AAP project sync before template "
            "(skill: Phase 1 - Prepare Playbook in Git Project)"
        )

    def test_privilege_escalation(self):
        """Skill: become_enabled is required for remediation templates
        (package updates need root). Without skill, agents may omit this."""
        c = read_report().lower()
        assert any(t in c for t in [
            "become", "privilege escalation", "escalat",
            "sudo", "root", "become_enabled",
        ]), (
            "should enable privilege escalation / become for remediation "
            "(skill: Phase 4 - Enable Privilege Escalation)"
        )

    def test_prompt_on_launch(self):
        """Skill: Template should enable Prompt on Launch for job type,
        variables, and limit for execution flexibility. Without skill,
        agents hardcode all settings."""
        c = read_report().lower()
        prompt_terms = sum(1 for t in [
            "prompt on launch", "prompt at launch",
            "ask_variables_on_launch", "ask_limit_on_launch",
            "prompt for", "ask on launch",
        ] if t in c)
        flexible_terms = sum(1 for t in [
            "variable", "limit", "job type",
        ] if t in c)
        assert prompt_terms >= 1 or flexible_terms >= 2, (
            "should configure prompt-on-launch for variables, limit, "
            "and job type (skill: Phase 4)"
        )

    def test_playbook_path_convention(self):
        """Skill: Playbooks follow the playbooks/remediation/ directory
        convention. Without skill, agents use arbitrary paths."""
        c = read_report().lower()
        assert any(t in c for t in [
            "playbooks/remediation",
            "remediation-cve",
            "playbook path",
            "playbook directory",
        ]), (
            "should follow playbook path convention "
            "(skill: playbooks/remediation/<filename>)"
        )
