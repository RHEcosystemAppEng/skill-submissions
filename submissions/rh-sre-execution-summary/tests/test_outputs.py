"""
Tests for rh-sre__execution-summary per-skill evaluation.

Skill-specific knowledge tested:
- Exact sentinel format: **** EXECUTION SUMMARY START/END ****
- Naming: rh-sre:<skill>, server:tool, docs/ path prefix
- Chronological order (not alphabetical)
- Compact format (no spaces after commas)
- Empty categories = "None"
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

    def test_mentions_topic(self):
        content = read_report().lower()
        assert any(t in content for t in ["summary", "execution", "skill"]), (
            "report should mention execution summary"
        )

    def test_report_has_structure(self):
        content = read_report()
        assert len(content) > 100, "execution summary should have content"


class TestSkillDependent:
    def test_sentinel_start_format(self):
        """Skill: Summary must start with exact sentinel
        '**** EXECUTION SUMMARY START ****'. Without skill, agents
        use generic headings or markdown headers."""
        c = read_report()
        assert "**** EXECUTION SUMMARY START ****" in c, (
            "should use exact sentinel: '**** EXECUTION SUMMARY START ****' "
            "(skill: machine-readable format)"
        )

    def test_sentinel_end_format(self):
        """Skill: Summary must end with exact sentinel
        '**** EXECUTION SUMMARY END ****'."""
        c = read_report()
        assert "**** EXECUTION SUMMARY END ****" in c, (
            "should use exact sentinel: '**** EXECUTION SUMMARY END ****' "
            "(skill: machine-readable format)"
        )

    def test_skill_naming_convention(self):
        """Skill: Skills use rh-sre:<name> prefix (e.g. rh-sre:fleet-inventory).
        Without skill, agents use bare names or inconsistent prefixes."""
        c = read_report()
        assert "rh-sre:" in c, (
            "should use rh-sre: prefix for skill names "
            "(skill: 'Include plugin prefix: rh-sre:')"
        )

    def test_tool_naming_convention(self):
        """Skill: Tools use server:tool format (e.g. lightspeed-mcp:get_cve).
        Without skill, agents list bare tool names."""
        c = read_report()
        has_server_prefix = any(t in c for t in [
            "lightspeed-mcp:", "aap-mcp-job-management:",
            "aap-mcp-inventory-management:",
        ])
        assert has_server_prefix, (
            "should use server:tool format for MCP tools "
            "(skill: 'Include server prefix')"
        )

    def test_doc_path_convention(self):
        """Skill: Docs use path from docs/ or skills/ onwards, not full
        filesystem paths. Without skill, agents use full paths or filenames."""
        c = read_report()
        has_docs_path = any(t in c for t in [
            "docs/insights/", "docs/ansible/", "docs/references/",
            "skills/playbook-generator/", "skills/fleet-inventory/",
        ])
        assert has_docs_path, (
            "should use docs/ or skills/ relative paths for documentation "
            "(skill: 'Path from docs/ onwards')"
        )

    def test_four_categories_present(self):
        """Skill: Summary must have all four categories: Agents, Skills,
        Tools, Docs. Without skill, agents use arbitrary categories."""
        c = read_report()
        has_agents = "Agents:" in c
        has_skills = "Skills:" in c
        has_tools = "Tools:" in c
        has_docs = "Docs:" in c
        assert has_agents and has_skills and has_tools and has_docs, (
            "should have all four categories: Agents, Skills, Tools, Docs "
            "(skill: standard template)"
        )

    def test_agents_none(self):
        """Skill: When no agents were invoked, category shows 'None'.
        The scenario had no agent invocations."""
        c = read_report()
        match = re.search(r"Agents:\s*(.*)", c)
        if match:
            agents_value = match.group(1).strip()
            assert agents_value.lower() == "none", (
                "Agents category should be 'None' when no agents were invoked"
            )

    def test_chronological_order(self):
        """Skill: Resources listed in chronological order of first use,
        NOT alphabetical. Without skill, agents alphabetize."""
        c = read_report()
        skills_match = re.search(r"Skills:\s*(.*)", c)
        if skills_match:
            skills_line = skills_match.group(1).strip()
            skills = [s.strip() for s in skills_line.split(",")]
            if len(skills) >= 3:
                validator_idx = next((i for i, s in enumerate(skills)
                                    if "validator" in s.lower()), None)
                fleet_idx = next((i for i, s in enumerate(skills)
                                 if "fleet" in s.lower() or "inventory" in s.lower()), None)
                cve_idx = next((i for i, s in enumerate(skills)
                               if "cve" in s.lower()), None)
                if validator_idx is not None and fleet_idx is not None:
                    assert validator_idx < fleet_idx, (
                        "skills should be in chronological order "
                        "(validator before fleet-inventory)"
                    )
