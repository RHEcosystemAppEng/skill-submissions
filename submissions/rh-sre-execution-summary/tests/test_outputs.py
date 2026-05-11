"""
Tests for rh-sre execution-summary skill evaluation.
Tests check for the specific structured output format defined in SKILL.md.
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
        assert len(content) > 100, "report should have substantial content"

    def test_mentions_cve(self):
        content = read_report().lower()
        assert "cve" in content, "report should mention CVE(s)"


class TestSkillDependent:
    def test_execution_summary_delimiters(self):
        """SKILL.md defines exact delimiters: **** EXECUTION SUMMARY START/END ****"""
        content = read_report()
        assert "EXECUTION SUMMARY START" in content, (
            "must use EXECUTION SUMMARY START delimiter (SKILL format)"
        )
        assert "EXECUTION SUMMARY END" in content, (
            "must use EXECUTION SUMMARY END delimiter (SKILL format)"
        )

    def test_four_categories_present(self):
        """SKILL.md requires exactly 4 categories: Agents, Skills, Tools, Docs"""
        content = read_report()
        start = content.find("EXECUTION SUMMARY START")
        end = content.find("EXECUTION SUMMARY END")
        if start == -1 or end == -1:
            pytest.fail("execution summary delimiters not found")
        block = content[start:end]
        categories_found = sum(1 for cat in ["Agents:", "Skills:", "Tools:", "Docs:"]
                               if cat in block)
        assert categories_found >= 3, (
            f"summary block must contain at least 3/4 categories "
            f"(Agents/Skills/Tools/Docs); found {categories_found}"
        )

    def test_skill_prefix_convention(self):
        """SKILL.md requires rh-sre: prefix for skills (e.g. rh-sre:fleet-inventory)"""
        content = read_report()
        assert "rh-sre:" in content, (
            "must use rh-sre: prefix for skill names (SKILL naming convention)"
        )

    def test_tool_prefix_convention(self):
        """SKILL.md requires server prefix for tools (e.g. lightspeed-mcp:get_host_details)"""
        content = read_report()
        has_tool_prefix = any(prefix in content for prefix in [
            "lightspeed-mcp:", "aap-mcp", "openshift-mcp:",
        ])
        assert has_tool_prefix, (
            "must use MCP server prefix for tool names "
            "(e.g. lightspeed-mcp:tool_name per SKILL convention)"
        )

    def test_specific_mcp_tools_referenced(self):
        """MCP exposes: get_host_details, get_cve_systems, get_cves, get_cve,
        create_vulnerability_playbook. A skilled agent uses and lists them."""
        content = read_report().lower()
        tools = ["get_host_details", "get_cve_systems", "get_cves", "get_cve",
                 "create_vulnerability_playbook"]
        found = sum(1 for t in tools if t in content)
        assert found >= 2, (
            f"should reference specific MCP tool names from the environment; "
            f"found {found}/5 expected tools"
        )

    def test_docs_category_path_format(self):
        """SKILL.md: docs should be paths from docs/ onwards or skills/*/SKILL.md"""
        content = read_report()
        has_doc_path = (
            re.search(r"docs/\S+\.md", content) is not None
            or re.search(r"skills/\S+/SKILL\.md", content) is not None
        )
        assert has_doc_path, (
            "Docs category should list paths from docs/ onwards "
            "(e.g. docs/ansible/playbook-templates.md per SKILL convention)"
        )

    def test_cve_specific_data_from_mcp(self):
        """MCP has 5 CVEs with specific IDs. A skilled agent queries and references them."""
        content = read_report()
        cve_ids = ["CVE-2024-12345", "CVE-2024-54321", "CVE-2024-11111",
                    "CVE-2024-98765", "CVE-2024-22222"]
        found = sum(1 for c in cve_ids if c in content)
        assert found >= 2, (
            f"should reference specific CVE IDs from MCP data; found {found}/5"
        )

    def test_remediation_workflow_skills_listed(self):
        """SKILL examples show remediation workflows invoke multiple rh-sre skills.
        A skilled agent should list several in the Skills line."""
        content = read_report().lower()
        skill_refs = [
            "fleet-inventory", "cve-impact", "cve-validation",
            "system-context", "playbook-generator", "playbook-executor",
            "execution-summary", "remediation", "job-template",
        ]
        found = sum(1 for s in skill_refs if s in content)
        assert found >= 2, (
            f"should list multiple rh-sre skills used during remediation; "
            f"found {found} skill references"
        )

    def test_compact_comma_format(self):
        """SKILL.md specifies compact format with no spaces after commas in lists."""
        content = read_report()
        start = content.find("EXECUTION SUMMARY START")
        end = content.find("EXECUTION SUMMARY END")
        if start == -1 or end == -1:
            pytest.skip("no execution summary block found")
        block = content[start:end]
        has_comma_list = re.search(r"rh-sre:\S+,rh-sre:\S+", block) is not None \
            or re.search(r"mcp:\S+,\S+mcp:\S+", block) is not None
        assert has_comma_list, (
            "summary lists should use compact comma-separated format (no spaces)"
        )
