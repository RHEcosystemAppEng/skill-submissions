"""
Tests for rh-developer-incident-triage per-skill evaluation.

Skill teaches Five Whys, investigation guardrails, Prometheus metric analysis,
and adversarial due diligence for multi-resource OpenShift incident triage.
Mock cluster has 3 namespaces with specific broken deployments.
"""
import os
import re
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
    def test_confidence_score(self):
        """Skill requires numeric confidence (0.XX). Control often omits."""
        c = read_report().lower()
        assert re.search(r'confidence[\s:]*[01]\.\d', c), (
            "must include numeric confidence score"
        )

    def test_five_whys_methodology(self):
        """Skill teaches Five Whys for causal reasoning. Without skill,
        agents jump to fixes without structured root cause analysis."""
        c = read_report().lower()
        assert "five whys" in c or "5 whys" in c or "causal chain" in c, (
            "must use Five Whys methodology"
        )

    def test_events_list_tool(self):
        """Skill teaches using events_list MCP tool to fetch Kubernetes
        events filtered by resource. Without skill, agents skip event
        correlation."""
        c = read_report()
        assert "events_list" in c or "events_list" in c.lower(), (
            "must reference events_list MCP tool for event correlation"
        )

    def test_get_metric_names_tool(self):
        """Skill teaches using observability MCP tools: get_metric_names,
        get_metric_metadata, query (PromQL). Without skill, agents don't
        query Prometheus metrics."""
        c = read_report()
        assert any(t in c for t in [
            "get_metric_names", "get_metric_metadata",
            "get_series", "PromQL", "promql",
        ]), "must reference observability MCP tools for Prometheus analysis"

    def test_mock_namespace_from_cluster(self):
        """Mock cluster has api-platform, web-frontend, order-system
        namespaces. Skilled agent discovers these via MCP."""
        c = read_report().lower()
        ns = ["api-platform", "web-frontend", "order-system"]
        found = sum(1 for n in ns if n in c)
        assert found >= 2, (
            "must reference namespaces discovered via MCP "
            "(api-platform, web-frontend, order-system)"
        )

    def test_oomkilled_exit_137(self):
        """Mock has web-frontend pod OOMKilled with 64Mi limit, exit code 137.
        Skilled agent identifies this from cluster data."""
        c = read_report()
        assert ("OOMKill" in c or "oom" in c.lower()) and (
            "137" in c or "64Mi" in c
        ), "must identify OOMKilled condition with exit code 137 or 64Mi limit"

    def test_selector_mismatch_diagnosis(self):
        """Mock has order-system Service selector mismatch: app=order-svc
        vs pod label app=order-service. Skill teaches tracing this."""
        c = read_report().lower()
        assert "order-svc" in c or ("selector" in c and "mismatch" in c), (
            "must diagnose selector mismatch in order-system"
        )
