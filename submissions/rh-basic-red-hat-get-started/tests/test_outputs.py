"""
Tests for rh-basic-red-hat-get-started per-skill evaluation.

Only differentiating tests kept — dead-weight tests where both
control and treatment pass have been removed.
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


class TestSkillDependent:
    def test_slash_commands(self):
        """Skill teaches the exact slash-command invocations for each
        installed skill (e.g., /red-hat-cve-explainer). Without skill,
        agents list skill names but not their invocation commands."""
        c = read_report()
        commands = [
            "/red-hat-cve-explainer",
            "/red-hat-diagnostics",
            "/red-hat-product-lifecycle",
            "/red-hat-security-mcp-setup",
            "/red-hat-support-severity",
        ]
        found = sum(1 for cmd in commands if cmd in c)
        assert found >= 4, (
            "must list at least 4 of 5 slash-command invocations"
        )

    def test_post_install_summary_format(self):
        """Skill teaches the exact post-install summary block with
        'Available commands:' heading. Without skill, agents produce
        generic summaries without the structured format."""
        c = read_report()
        assert "Available commands" in c or "available commands" in c.lower(), (
            "must include 'Available commands' post-install summary"
        )

    def test_security_mcp_setup_recommendation(self):
        """Skill teaches recommending /red-hat-security-mcp-setup as
        the first post-install action. Without skill, agents don't
        know which skill to run first."""
        c = read_report()
        assert "/red-hat-security-mcp-setup" in c and (
            "first" in c.lower() or "configure" in c.lower() or "type" in c.lower()
        ), "must recommend /red-hat-security-mcp-setup as first step"

    def test_raw_download_methodology(self):
        """Skill teaches downloading raw files directly without reading
        and re-writing content (to avoid truncation). Without skill,
        agents describe generic file operations."""
        c = read_report().lower()
        assert "raw" in c or "direct" in c and "download" in c or (
            "truncat" in c or "re-writ" in c or "reformat" in c
        ), "must describe raw download methodology (not read+rewrite)"

    def test_self_destruct_confirmation(self):
        """Skill teaches the self-destruct pattern: delete installer
        directory and confirm removal. Without skill, agents don't
        include the deletion confirmation step."""
        c = read_report().lower()
        has_destruct = "self-destruct" in c or "removed itself" in c
        has_delete = "delet" in c and ("installer" in c or "get-started" in c)
        assert has_destruct or has_delete, (
            "must describe installer self-destruct and confirm removal"
        )

    def test_skill_descriptions(self):
        """Skill teaches specific one-line descriptions for each command
        (e.g., 'Explain a CVE', 'Gather diagnostic data'). Without
        skill, agents produce generic summaries."""
        c = read_report().lower()
        descriptions = [
            "explain a cve", "diagnostic data",
            "lifecycle status", "security mcp server",
            "support ticket severity", "sla",
        ]
        found = sum(1 for d in descriptions if d in c)
        assert found >= 3, (
            "must include specific skill descriptions from installer"
        )
