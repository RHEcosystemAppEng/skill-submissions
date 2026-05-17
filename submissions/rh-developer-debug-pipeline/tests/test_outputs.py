"""
Tests for rh-developer-debug-pipeline per-skill evaluation.

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

    def test_tekton_crd_api_version(self):
        """Skill teaches the exact apiVersion tekton.dev/v1 for
        PipelineRun/TaskRun CRDs. Without skill, agents may use
        wrong version or omit it."""
        c = read_report()
        assert "tekton.dev/v1" in c, (
            "must reference tekton.dev/v1 apiVersion"
        )

    def test_status_child_references(self):
        """Skill teaches extracting task statuses from PipelineRun
        .status.childReferences field path. Without skill, agents
        don't know this specific status structure."""
        c = read_report()
        assert "childReferences" in c or "taskRuns" in c, (
            "must reference .status.childReferences or .status.taskRuns"
        )
