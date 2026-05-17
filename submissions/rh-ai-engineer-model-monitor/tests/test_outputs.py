"""
Tests for rh-ai-engineer-model-monitor per-skill evaluation.

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
    def test_mcp_tool_resources_create_or_update(self):
        """Skill teaches using resources_create_or_update MCP tool to create
        TrustyAIService CR and metric ConfigMaps. Without skill, agents
        describe generic kubectl or manual steps."""
        c = read_report()
        assert "resources_create_or_update" in c, (
            "must reference resources_create_or_update MCP tool"
        )

    def test_trustyai_cr_api_version(self):
        """Skill teaches the exact apiVersion trustyai.opendatahub.io/v1alpha1
        for the TrustyAIService CR. Without skill, agents omit or guess."""
        c = read_report()
        assert "trustyai.opendatahub.io/v1alpha1" in c, (
            "must reference trustyai.opendatahub.io/v1alpha1 apiVersion"
        )

    def test_prometheus_query_tool(self):
        """Skill teaches using prometheus_query MCP tool to validate
        TrustyAI metrics. Without skill, agents describe manual PromQL."""
        c = read_report()
        assert "prometheus_query" in c, (
            "must reference prometheus_query MCP tool for metrics validation"
        )
