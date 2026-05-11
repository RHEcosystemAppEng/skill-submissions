"""
Tests for rh-sre playbook-generator skill evaluation.
Tests check for the specific generation workflow from SKILL.md.
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

    def test_mentions_cve(self):
        content = read_report().lower()
        assert "cve" in content, "report should mention CVE"


class TestSkillDependent:
    def test_playbook_yaml_content(self):
        """SKILL: return playbook YAML from MCP tool. Report should include playbook content."""
        c = read_report().lower()
        yaml_markers = sum(1 for m in [
            "---", "hosts:", "tasks:", "become:", "name:",
            "dnf:", "yum:", "ansible", "playbook",
        ] if m in c)
        assert yaml_markers >= 3, (
            "report should include generated playbook YAML content"
        )

    def test_mcp_tool_create_vulnerability_playbook(self):
        """SKILL: must use create_vulnerability_playbook MCP tool."""
        c = read_report().lower()
        has_tool = any(t in c for t in [
            "create_vulnerability_playbook", "create_vuln_playbook",
            "remediations__create", "lightspeed",
        ])
        assert has_tool, (
            "must reference create_vulnerability_playbook MCP tool "
            "(SKILL primary tool)"
        )

    def test_return_as_is_principle(self):
        """SKILL: CRITICAL - return playbook AS IS from MCP. Do NOT modify."""
        c = read_report().lower()
        has_as_is = any(t in c for t in [
            "as is", "as-is", "unmodified", "without modification",
            "as provided", "returned as", "original playbook",
            "do not modify", "not modified",
        ])
        assert has_as_is, (
            "should note playbook is returned as-is from MCP tool "
            "(SKILL CRITICAL requirement)"
        )

    def test_generation_only_not_execution(self):
        """SKILL: ONLY GENERATES. Does NOT execute. Must delegate to playbook-executor."""
        c = read_report().lower()
        has_no_exec = any(t in c for t in [
            "does not execute", "do not execute", "not execute",
            "generation only", "generate only",
            "playbook-executor", "hand off", "handoff",
        ])
        assert has_no_exec, (
            "must clarify this is generation-only, not execution "
            "(SKILL CRITICAL SCOPE LIMITATION)"
        )

    def test_error_handling_options(self):
        """SKILL: if tool fails, present A/B/C options (retry/generate from knowledge/exit)."""
        c = read_report().lower()
        has_error = any(t in c for t in [
            "retry", "generate from knowledge", "exit",
            "option a", "option b", "option c",
            "if.*fail", "error handling", "tool fail",
            "alternative approach",
        ])
        assert has_error, (
            "should describe error handling when MCP tool fails "
            "(SKILL: retry/knowledge/exit options)"
        )

    def test_cve_specific_targeting(self):
        """Report should reference specific CVE ID from the task scenario."""
        c = read_report()
        has_cve = bool(re.search(r"CVE-\d{4}-\d+", c))
        assert has_cve, "should reference specific CVE ID(s)"

    def test_affected_systems_from_mcp(self):
        """MCP data identifies affected systems. Skilled agent references them."""
        c = read_report().lower()
        has_systems = any(t in c for t in [
            "affected system", "target system", "production system",
            "web-server", "db-server", "app-server",
            "vulnerable", "system_id",
        ])
        assert has_systems, (
            "should reference affected systems from MCP data"
        )

    def test_playbook_metadata(self):
        """SKILL: document playbook metadata (target CVE, reboot, packages)."""
        c = read_report().lower()
        meta = sum(1 for m in [
            "reboot", "restart", "package", "update",
            "kernel", "severity", "critical", "target",
        ] if m in c)
        assert meta >= 2, (
            "should document playbook metadata (packages, reboot, target CVE)"
        )
