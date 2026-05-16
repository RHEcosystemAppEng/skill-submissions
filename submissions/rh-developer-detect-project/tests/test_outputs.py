"""
Tests for rh-developer-detect-project per-skill evaluation.

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
    def test_app_module_format(self):
        """Skill teaches APP_MODULE format 'module:callable' (e.g., app:app)
        for S2I Python. Without skill, agents don't know this S2I builder
        configuration variable."""
        c = read_report()
        assert "APP_MODULE" in c or "app_module" in c.lower(), (
            "must specify APP_MODULE configuration for S2I Python"
        )

    def test_s2i_entry_point_detection_order(self):
        """Skill teaches the S2I Python entry point detection order:
        app.sh -> application.py -> app.py. Without skill, agents
        don't describe the builder's startup sequence."""
        c = read_report().lower()
        has_sequence = "app.sh" in c
        has_detection = "entry point" in c and ("detection" in c or "order" in c or "app.py" in c)
        has_startup = "startup" in c and ("sequence" in c or "order" in c)
        assert has_sequence or has_detection or has_startup, (
            "must describe S2I Python entry point detection "
            "(app.sh / application.py / app.py sequence)"
        )

    def test_gunicorn_s2i_coupling(self):
        """Skill teaches that gunicorn must be in requirements.txt for
        the S2I Python builder to use APP_MODULE. Without skill, agents
        mention gunicorn generically without the S2I connection."""
        c = read_report().lower()
        assert "gunicorn" in c and ("s2i" in c or "app_module" in c or "builder" in c), (
            "must connect gunicorn to S2I/APP_MODULE builder requirement"
        )

    def test_chart_yaml_helm_detection(self):
        """Skill teaches checking for Chart.yaml as primary Helm detection
        signal, with specific search order. Without skill, agents don't
        systematically detect Helm charts."""
        c = read_report()
        assert "Chart.yaml" in c or "chart.yaml" in c.lower() or (
            "helm" in c.lower() and "chart" in c.lower() and "detect" in c.lower()
        ), "must describe Helm chart detection via Chart.yaml"

    def test_builder_image_output_variable(self):
        """Skill teaches producing structured output variables like
        BUILDER_IMAGE and BUILD_STRATEGY. Without skill, agents write
        prose without structured detection results."""
        c = read_report()
        assert "BUILDER_IMAGE" in c or "BUILD_STRATEGY" in c or "CONTAINER_PORT" in c, (
            "must produce structured output variables "
            "(BUILDER_IMAGE, BUILD_STRATEGY, CONTAINER_PORT)"
        )

    def test_mock_app_metadata(self):
        """Skill-equipped agents use MCP to discover app metadata from
        the cluster (inventory-api, customer-portal). Without skill,
        agents analyze only local files."""
        c = read_report().lower()
        apps = ["inventory-api", "customer-portal", "payment-processor"]
        found = sum(1 for a in apps if a in c)
        assert found >= 1, (
            "must reference cluster app metadata discovered via MCP"
        )
