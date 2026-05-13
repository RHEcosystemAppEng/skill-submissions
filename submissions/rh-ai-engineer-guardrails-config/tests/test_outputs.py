"""
Tests for rh-ai-engineer-guardrails-config per-skill evaluation.

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
        the GuardrailsOrchestrator CR and detector ConfigMap. Without skill,
        agents describe generic kubectl apply or manual steps."""
        c = read_report()
        assert "resources_create_or_update" in c, (
            "must reference resources_create_or_update MCP tool"
        )

    def test_orchestrator_config_field(self):
        """Skill teaches the orchestratorConfig field that links the
        GuardrailsOrchestrator CR to its detector ConfigMap. Without skill,
        agents don't know this CR field name."""
        c = read_report()
        assert "orchestratorConfig" in c, (
            "must reference orchestratorConfig CR field"
        )

    def test_enable_built_in_detectors(self):
        """Skill teaches enableBuiltInDetectors and enableGuardrailsGateway
        as key CR spec fields. Without skill, agents don't know the exact
        boolean field names in the CRD spec."""
        c = read_report()
        has_builtin = "enableBuiltInDetectors" in c
        has_gateway = "enableGuardrailsGateway" in c
        assert has_builtin or has_gateway, (
            "must reference enableBuiltInDetectors or enableGuardrailsGateway"
        )

    def test_trustyai_cr_api_version(self):
        """Skill teaches the exact apiVersion trustyai.opendatahub.io/v1alpha1
        for the GuardrailsOrchestrator CR. Without skill, agents guess or
        omit the version."""
        c = read_report()
        assert "trustyai.opendatahub.io/v1alpha1" in c, (
            "must reference trustyai.opendatahub.io/v1alpha1 apiVersion"
        )

    def test_resources_list_for_crd_discovery(self):
        """Skill teaches using resources_list MCP tool with
        apiextensions.k8s.io/v1 to verify CRD availability. Without skill,
        agents skip CRD verification or use kubectl."""
        c = read_report()
        has_resources_list = "resources_list" in c
        has_apiext = "apiextensions.k8s.io" in c
        assert has_resources_list or has_apiext, (
            "must reference resources_list or apiextensions.k8s.io for CRD check"
        )
