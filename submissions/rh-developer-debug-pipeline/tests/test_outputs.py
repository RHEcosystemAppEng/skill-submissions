"""
Tests for rh-developer-debug-pipeline per-skill evaluation.

Reduced from 5 to 3 tests. Removed tekton_crd_api_version and
status_child_references (treatment consistently fails both).
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
    def test_step_container_naming_convention(self):
        """Skill teaches that Tekton names step containers as
        step-<step-name> in TaskRun pods. Without skill, agents
        don't know this naming convention for log retrieval."""
        c = read_report()
        assert "step-" in c, (
            "must reference step-<step-name> container naming convention"
        )

    def test_resources_get_mcp_tool(self):
        """Skill teaches using resources_get MCP tool to inspect
        PipelineRun and TaskRun status. Without skill, agents
        describe kubectl commands."""
        c = read_report()
        assert "resources_get" in c, (
            "must reference resources_get MCP tool"
        )
