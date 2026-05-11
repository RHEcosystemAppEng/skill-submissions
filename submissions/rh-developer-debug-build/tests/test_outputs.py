"""
Tests for rh-developer__debug-build per-skill evaluation.
Baseline tests: report structure.
Skill-dependent tests: check for knowledge from SKILL.md, docs/debugging-patterns.md,
docs/python-s2i-entrypoints.md, and docs/builder-images.md that an unskilled agent
would not know.
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

    def test_mentions_build(self):
        content = read_report().lower()
        assert "build" in content, "report should mention builds"

    def test_report_has_structure(self):
        content = read_report()
        assert len(content) > 150, "report should have substantial content"


class TestSkillDependent:
    def test_s2i_entry_point_detection_order(self):
        """SKILL.md + python-s2i-entrypoints.md teaches the S2I Python run script
        checks: app.sh -> gunicorn+APP_MODULE -> app.py -> error.
        The mock shows api-service uses main.py (not app.py) without gunicorn,
        so a skilled agent identifies this specific startup sequence."""
        c = read_report().lower()
        has_sequence = (
            ("app.sh" in c and "app.py" in c)
            or "entry point" in c and "main.py" in c
            or ("app_module" in c and "main" in c)
        )
        assert has_sequence, (
            "should identify S2I Python startup detection order "
            "(app.sh -> gunicorn+APP_MODULE -> app.py)"
        )

    def test_app_module_env_var_fix(self):
        """python-s2i-entrypoints.md teaches APP_MODULE=module:variable format.
        The fix for api-service requires setting APP_MODULE=main:app (or similar)
        plus installing gunicorn. An unskilled agent won't know APP_MODULE format."""
        c = read_report()
        assert "APP_MODULE" in c, (
            "should recommend setting APP_MODULE environment variable "
            "(the S2I Python mechanism for non-app.py entry points)"
        )

    def test_gunicorn_requirement(self):
        """python-s2i-entrypoints.md teaches gunicorn is required when APP_MODULE
        is used. The mock build log shows gunicorn is not installed. A skilled agent
        knows to add gunicorn to requirements.txt."""
        c = read_report().lower()
        assert "gunicorn" in c, (
            "should identify that gunicorn must be added to requirements.txt "
            "for APP_MODULE to work"
        )

    def test_s2i_custom_assemble_script(self):
        """SKILL.md teaches creating .s2i/bin/assemble to extend the S2I build.
        For psycopg2 pg_config failure, a skilled agent recommends a custom
        assemble script that installs system packages before pip install."""
        c = read_report()
        assert ".s2i/bin/assemble" in c or ".s2i/bin" in c, (
            "should mention .s2i/bin/assemble as a way to customize the S2I build "
            "(e.g. to install system dependencies like pg_config)"
        )

    def test_default_assemble_path(self):
        """SKILL.md + docs reference the default S2I assemble at /usr/libexec/s2i/assemble.
        A custom .s2i/bin/assemble should call the original. An unskilled agent
        doesn't know this path."""
        c = read_report()
        assert "/usr/libexec/s2i/" in c or "libexec/s2i" in c, (
            "should reference the default S2I assemble script at /usr/libexec/s2i/ "
            "(to chain custom assemble with the original)"
        )

    def test_s2i_phase_identification(self):
        """debugging-patterns.md teaches 5 S2I build phases: fetch-source,
        pull-builder, assemble, commit, push. A skilled agent identifies which
        phase failed (assemble for api-service-2)."""
        c = read_report().lower()
        assert "assemble" in c and any(
            w in c for w in ["phase", "step", "stage"]
        ), (
            "should identify the failing S2I build phase (assemble) using "
            "the phase-by-phase diagnosis from debugging-patterns.md"
        )

    def test_pg_config_psycopg2_binary_fix(self):
        """The build log shows psycopg2 failing because pg_config is missing.
        A skilled agent knows the standard fix: use psycopg2-binary (pre-compiled)
        instead of psycopg2 (requires C compiler + pg_config)."""
        c = read_report().lower()
        assert "psycopg2-binary" in c or "psycopg2[binary]" in c or (
            "binary" in c and "psycopg" in c
        ), (
            "should recommend psycopg2-binary as the fix for pg_config not found "
            "(pre-compiled wheel, no system dependencies needed)"
        )

    def test_service_selector_mismatch(self):
        """The order-system Service uses selector app=order-svc but pods have
        label app=order-service. debugging-patterns.md teaches checking selector
        vs pod labels. A skilled agent catches this mismatch."""
        c = read_report().lower()
        has_mismatch = (
            ("order-svc" in c and "order-service" in c)
            or "selector" in c and "mismatch" in c
            or "selector" in c and "label" in c
        )
        assert has_mismatch, (
            "should identify the service selector mismatch "
            "(order-svc vs order-service) causing 503 errors"
        )
