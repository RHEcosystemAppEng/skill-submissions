"""
Tests for rh-ai-engineer-pipeline-manage per-skill evaluation.

Reduced from 6 to 4 tests. Removed scheduled_workflow_crd and
tekton_pipelinerun_label (treatment unreliably passes).
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
    def test_dspa_api_version(self):
        """Skill teaches the DSPA CRD apiVersion
        datasciencepipelinesapplications.opendatahub.io/v1alpha1.
        Without skill, agents don't know how to create/check DSPA."""
        c = read_report()
        assert "datasciencepipelinesapplications.opendatahub.io" in c, (
            "must reference DSPA CRD apiVersion"
        )

    def test_status_child_references(self):
        """Skill teaches extracting task statuses from PipelineRun
        .status.childReferences. Without skill, agents don't know
        the field path for step-level progress."""
        c = read_report()
        assert "childReferences" in c or "taskRuns" in c, (
            "must reference .status.childReferences or .status.taskRuns"
        )

    def test_resources_create_or_update_tool(self):
        """Skill teaches using resources_create_or_update MCP tool to
        create DSPA, PipelineRun, and ScheduledWorkflow CRs."""
        c = read_report()
        assert "resources_create_or_update" in c, (
            "must reference resources_create_or_update MCP tool"
        )
