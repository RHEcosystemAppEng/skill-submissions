"""
Tests for rh-basic-red-hat-get-started per-skill evaluation.

Only differentiating tests kept — dead-weight tests where both
control and treatment pass 3/3 have been removed.
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
    def test_skills_repo_url(self):
        """Skill teaches the exact SKILLS_REPO URL pointing to
        agentic-collections/tree/main/rh-basic/skills. Without skill,
        agents don't know where to fetch skills from."""
        c = read_report()
        assert "agentic-collections" in c, (
            "must reference agentic-collections repo"
        )

    def test_red_hat_cve_explainer_skill(self):
        """Skill teaches installing red-hat-cve-explainer as one of
        the 5 specific skills. Without skill, agents don't know the
        exact skill names."""
        c = read_report()
        assert "red-hat-cve-explainer" in c or "cve-explainer" in c, (
            "must reference red-hat-cve-explainer skill"
        )

    def test_red_hat_security_mcp_setup_skill(self):
        """Skill teaches installing red-hat-security-mcp-setup as one
        of the 5 skills, and recommending it as first post-install step."""
        c = read_report()
        assert "red-hat-security-mcp-setup" in c or "security-mcp-setup" in c, (
            "must reference red-hat-security-mcp-setup skill"
        )

    def test_self_destruct_behavior(self):
        """Skill teaches self-destructing after installation — removing
        its own directory. Without skill, agents don't know this pattern."""
        c = read_report()
        has_self = "self-destruct" in c.lower() or "removed itself" in c.lower()
        has_remove = "remove" in c.lower() and "installer" in c.lower()
        assert has_self or has_remove, (
            "must reference installer self-destruct behavior"
        )

    def test_five_specific_skills(self):
        """Skill teaches exactly 5 skills to install. Without skill,
        agents don't know the full list."""
        c = read_report().lower()
        count = sum(1 for s in [
            "cve-explainer", "diagnostics", "product-lifecycle",
            "security-mcp-setup", "support-severity"
        ] if s in c)
        assert count >= 4, (
            "must reference at least 4 of 5 specific skill names"
        )
