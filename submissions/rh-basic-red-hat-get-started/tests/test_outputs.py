"""
Tests for rh-basic-red-hat-get-started per-skill evaluation.

Kept only tests whose assertions rely on SKILL.md-specific knowledge
(exact format strings, workflow steps) that the instruction alone
does not reveal.
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

    def test_post_install_summary_format(self):
        """Skill teaches the exact post-install summary block with
        'Available commands:' heading. Without skill, agents produce
        generic summaries without the structured format."""
        c = read_report()
        assert "Available commands" in c or "available commands" in c.lower(), (
            "must include 'Available commands' post-install summary"
        )
