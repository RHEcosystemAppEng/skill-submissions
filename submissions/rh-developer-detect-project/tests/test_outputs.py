"""
Tests for rh-developer-detect-project per-skill evaluation.

Reduced to strongest differentiating tests. Removed tests where both
agents fail equally (s2i_entry_point, chart_yaml, builder_image_output).
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

    def test_gunicorn_s2i_coupling(self):
        """Skill teaches that gunicorn must be in requirements.txt for
        the S2I Python builder to use APP_MODULE. Without skill, agents
        mention gunicorn generically without the S2I connection."""
        c = read_report().lower()
        assert "gunicorn" in c and ("s2i" in c or "app_module" in c or "builder" in c), (
            "must connect gunicorn to S2I/APP_MODULE builder requirement"
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
