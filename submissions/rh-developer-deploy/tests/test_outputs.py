"""
Tests for rh-developer-deploy per-skill evaluation.

Reduced from 5 to 4 tests. Removed selector_mismatch_diagnosis
(both agents fail equally).
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
    def test_port_detection_methodology(self):
        """Skill teaches systematic port detection: Dockerfile EXPOSE,
        web server config, framework defaults (Flask 5000, Node 3000).
        Without skill, agents hardcode 8080 without detection logic."""
        c = read_report().lower()
        methods = ["expose", "framework default", "flask", "5000", "3000"]
        found = sum(1 for m in methods if m in c)
        assert found >= 2, (
            "must describe port detection methodology "
            "(Dockerfile EXPOSE, framework defaults, etc.)"
        )

    def test_mock_namespace_discovery(self):
        """Skill-equipped agents use MCP to discover cluster state and
        reference actual namespaces. Without skill, agents write generic
        plans without cluster-specific context."""
        c = read_report().lower()
        ns = ["api-platform", "web-frontend", "order-system"]
        found = sum(1 for n in ns if n in c)
        assert found >= 2, (
            "must reference cluster namespaces discovered via MCP"
        )

    def test_resources_create_or_update_tool(self):
        """Skill teaches using resources_create_or_update MCP tool to
        apply manifests. Without skill, agents describe oc apply/create
        without MCP tool context."""
        c = read_report()
        assert "resources_create_or_update" in c or "create_or_update" in c or (
            "MCP" in c and "resource" in c.lower()
        ), "must reference resources_create_or_update MCP tool or MCP-based resource creation"
