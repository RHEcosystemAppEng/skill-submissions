"""
Tests for rh-ai-engineer-pipeline-manage per-skill evaluation.

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
    def test_dspa_api_version(self):
        """Skill teaches the DSPA CRD apiVersion
        datasciencepipelinesapplications.opendatahub.io/v1alpha1.
        Without skill, agents don't know how to create/check DSPA."""
        c = read_report()
        assert "datasciencepipelinesapplications.opendatahub.io" in c, (
            "must reference DSPA CRD apiVersion"
        )

    def test_scheduled_workflow_crd(self):
        """Skill teaches ScheduledWorkflow CRD from
        scheduledworkflows.kubeflow.org/v1beta1 for recurring runs.
        Without skill, agents describe generic cron jobs."""
        c = read_report()
        assert "ScheduledWorkflow" in c or "scheduledworkflows.kubeflow.org" in c, (
            "must reference ScheduledWorkflow CRD for recurring pipeline runs"
        )

    def test_status_child_references(self):
        """Skill teaches extracting task statuses from PipelineRun
        .status.childReferences. Without skill, agents don't know
        the field path for step-level progress."""
        c = read_report()
        assert "childReferences" in c or "taskRuns" in c, (
            "must reference .status.childReferences or .status.taskRuns"
        )

    def test_tekton_pipelinerun_label(self):
        """Skill teaches using labelSelector tekton.dev/pipelineRun to
        find pipeline step pods. Without skill, agents list all pods."""
        c = read_report()
        assert "tekton.dev/pipelineRun" in c, (
            "must reference tekton.dev/pipelineRun label selector"
        )

    def test_resources_create_or_update_tool(self):
        """Skill teaches using resources_create_or_update MCP tool to
        create DSPA, PipelineRun, and ScheduledWorkflow CRs."""
        c = read_report()
        assert "resources_create_or_update" in c, (
            "must reference resources_create_or_update MCP tool"
        )
