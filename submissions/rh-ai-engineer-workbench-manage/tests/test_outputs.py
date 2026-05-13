"""
Tests for rh-ai-engineer-workbench-manage per-skill evaluation.

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
    def test_notebook_cr_kind(self):
        """Skill teaches Notebook CR (kubeflow.org/v1) as the underlying
        resource for RHOAI workbenches. Without skill, agents describe
        the dashboard UI or generic pod creation."""
        c = read_report()
        assert "kubeflow.org/v1" in c or "kind: Notebook" in c or "Notebook CR" in c, (
            "must reference kubeflow.org/v1 Notebook CR"
        )

    def test_kubeflow_resource_stopped_annotation(self):
        """Skill teaches kubeflow-resource-stopped annotation to stop/start
        workbenches. Without skill, agents don't know this mechanism."""
        c = read_report()
        assert "kubeflow-resource-stopped" in c, (
            "must reference kubeflow-resource-stopped annotation for stop/start"
        )

    def test_notebook_image_label(self):
        """Skill teaches discovering notebook images via ImageStream with
        label opendatahub.io/notebook-image=true. Without skill, agents
        use generic image references."""
        c = read_report()
        has_label = "opendatahub.io/notebook-image" in c
        has_imagestream = "ImageStream" in c and "redhat-ods-applications" in c
        assert has_label or has_imagestream, (
            "must reference notebook image discovery via opendatahub.io/notebook-image label"
        )

    def test_rhoai_mcp_workbench_tools(self):
        """Skill teaches using create_workbench / start_workbench /
        stop_workbench MCP tools from rhoai server. Without skill,
        agents use generic kubectl."""
        c = read_report()
        has_create = "create_workbench" in c
        has_start = "start_workbench" in c
        has_stop = "stop_workbench" in c
        assert has_create or has_start or has_stop, (
            "must reference rhoai MCP workbench tools"
        )

    def test_image_openshift_io_imagestream(self):
        """Skill teaches browsing image.openshift.io/v1 ImageStreams to
        discover available notebook images and tags. Without skill,
        agents hardcode image references."""
        c = read_report()
        assert "image.openshift.io" in c or "ImageStream" in c, (
            "must reference image.openshift.io ImageStream for image discovery"
        )
