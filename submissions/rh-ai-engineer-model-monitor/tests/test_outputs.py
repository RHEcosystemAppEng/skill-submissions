"""
Tests for rh-ai-engineer-model-monitor per-skill evaluation.

Kept MCP-tool checks that differentiate; removed trustyai apiVersion (both pass 100%).
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
    def test_mcp_tool_resources_create_or_update(self):
        """Skill teaches resources_create_or_update MCP tool."""
        c = read_report()
        assert "resources_create_or_update" in c, (
            "must reference resources_create_or_update MCP tool"
        )

    def test_prometheus_query_tool(self):
        """Skill teaches prometheus_query MCP tool for metrics validation."""
        c = read_report()
        assert "prometheus_query" in c, (
            "must reference prometheus_query MCP tool for metrics validation"
        )
