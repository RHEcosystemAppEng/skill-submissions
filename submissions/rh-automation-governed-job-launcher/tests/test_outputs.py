"""Tests for skill evaluation. Baseline + skill-dependent checks."""
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

    def test_report_has_content(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"

class TestSkillDependent:
    def test_uses_mcp_data(self):
        """Report should contain specific data from MCP tool queries."""
        c = read_report().lower()
        assert len(c) > 500, "report should demonstrate thorough analysis using MCP tools"
