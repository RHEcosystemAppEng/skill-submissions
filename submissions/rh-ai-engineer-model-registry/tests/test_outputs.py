"""
Tests for rh-ai-engineer-model-registry per-skill evaluation.

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
    def test_model_registry_api_version(self):
        """Skill teaches the exact apiVersion modelregistry.opendatahub.io/v1alpha1
        for RegisteredModel, ModelVersion, ModelArtifact CRs. Without skill,
        agents don't know the CRD group."""
        c = read_report()
        assert "modelregistry.opendatahub.io/v1alpha1" in c, (
            "must reference modelregistry.opendatahub.io/v1alpha1"
        )

    def test_resources_create_or_update_tool(self):
        """Skill teaches using resources_create_or_update MCP tool to create
        RegisteredModel, ModelVersion, and ModelArtifact CRs."""
        c = read_report()
        assert "resources_create_or_update" in c, (
            "must reference resources_create_or_update MCP tool"
        )

    def test_registered_model_cr_kind(self):
        """Skill teaches RegisteredModel as the Kubernetes CR kind for
        model registration. Without skill, agents describe REST APIs."""
        c = read_report()
        assert "RegisteredModel" in c, (
            "must reference RegisteredModel CR kind"
        )

    def test_spec_custom_properties(self):
        """Skill teaches spec.customProperties for adding metadata to
        RegisteredModel CRs. Without skill, agents use generic annotations."""
        c = read_report()
        assert "customProperties" in c, (
            "must reference spec.customProperties field"
        )

    def test_model_version_id_linking(self):
        """Skill teaches spec.registeredModelId to link ModelVersion to
        RegisteredModel, and spec.modelVersionId to link ModelArtifact
        to ModelVersion."""
        c = read_report()
        has_reg = "registeredModelId" in c
        has_ver = "modelVersionId" in c
        assert has_reg or has_ver, (
            "must reference registeredModelId or modelVersionId for CR linking"
        )
