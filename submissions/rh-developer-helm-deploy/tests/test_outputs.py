"""
Tests for rh-developer-helm-deploy per-skill evaluation.

Only differentiating tests kept — dead-weight tests where both
control and treatment pass have been removed.
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
    def test_helm_list_existing_releases(self):
        """Skill teaches checking existing releases via helm_list before
        deploying. Without skill, agents jump to helm install without
        checking for existing releases."""
        c = read_report().lower()
        assert "helm_list" in c or "helm list" in c or (
            "existing" in c and "release" in c
        ), "must check existing Helm releases before deploying"

    def test_helm_upgrade_vs_install(self):
        """Skill teaches using helm_upgrade (with --install) when a
        release already exists, vs helm_install for new deployments.
        Without skill, agents always use install."""
        c = read_report().lower()
        assert ("upgrade" in c and "install" in c) or "helm_upgrade" in c, (
            "must address upgrade vs install decision for existing releases"
        )

    def test_mock_release_names(self):
        """Skill-equipped agents discover existing releases from the
        cluster (api-service, web-frontend). Without skill, agents
        write generic plans without cluster context."""
        c = read_report().lower()
        releases = ["api-service", "web-frontend"]
        found = sum(1 for r in releases if r in c)
        assert found >= 1, (
            "must reference existing Helm releases discovered via MCP"
        )

    def test_route_openshift_template(self):
        """Skill teaches including route.openshift.io/v1 Route in Helm
        chart templates for OpenShift. Without skill, agents use
        generic Ingress without Route awareness."""
        c = read_report()
        assert "route.openshift.io" in c or (
            "Route" in c and ("template" in c.lower() or "chart" in c.lower())
        ), "must include OpenShift Route in chart templates"

    def test_values_from_mock(self):
        """Skill-equipped agents reference values from the mock Helm
        chart (route.enabled, service.port, resources.limits).
        Without skill, agents write generic values."""
        c = read_report().lower()
        values = ["route.enabled", "service.port", "resources.limits"]
        found = sum(1 for v in values if v in c)
        assert found >= 1, (
            "must reference specific values from chart "
            "(route.enabled, service.port, resources.limits)"
        )

    def test_detect_project_context(self):
        """Skill teaches reusing /detect-project session variables
        (HELM_CHART_PATH, BUILD_STRATEGY) when available. Without
        skill, agents don't know the skill chain."""
        c = read_report().lower()
        assert "detect-project" in c or "helm_chart_path" in c or (
            "detect" in c and "project" in c and "chart" in c
        ), "must reference detect-project context or HELM_CHART_PATH"
