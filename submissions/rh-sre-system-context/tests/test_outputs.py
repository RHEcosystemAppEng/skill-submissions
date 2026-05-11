"""
Tests for rh-sre system-context skill evaluation.
Baseline tests: report structure.
Skill-dependent tests: check for knowledge exclusive to SKILL.md + MCP data.
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

    def test_mentions_topic(self):
        content = read_report().lower()
        assert any(t in content for t in ["system", "context", "environment"]), (
            "report should mention key topic"
        )

    def test_report_has_structure(self):
        content = read_report()
        assert len(content) > 150, "report should have substantial content"


class TestSkillDependent:
    def test_compliance_tags_from_mcp(self):
        """MCP returns pci-compliant, hipaa-compliant, soc2-compliant tags.
        Only a skilled agent using MCP tools discovers these."""
        c = read_report().lower()
        assert any(t in c for t in [
            "pci-compliant", "pci compliant", "pci",
            "hipaa-compliant", "hipaa compliant", "hipaa",
            "soc2-compliant", "soc2 compliant", "soc2",
        ]), "should report compliance tags from MCP inventory (pci/hipaa/soc2)"

    def test_stale_system_detection(self):
        """MCP data includes stale=True systems (last_seen >7 days).
        SKILL.md doesn't mention stale but MCP data exposes it."""
        c = read_report().lower()
        assert any(t in c for t in [
            "stale", "last seen", "last_seen", "unreachable",
            "not reporting", "offline", "check-in",
        ]), "should identify stale/unreachable systems from MCP data"

    def test_rhel_version_mix_specifics(self):
        """MCP has systems on RHEL 8.8, 8.9, 9.2, 9.3.
        SKILL teaches conditional dnf/yum for multi-version."""
        c = read_report().lower()
        versions_found = sum(1 for v in ["8.8", "8.9", "9.2", "9.3"] if v in c)
        assert versions_found >= 2, (
            "should report specific RHEL versions from MCP (8.8/8.9/9.2/9.3)"
        )

    def test_environment_breakdown_with_counts(self):
        """MCP has 30 prod, 15 staging, 10 dev, 5 QA, 3 legacy.
        SKILL teaches environment classification for rollout order."""
        c = read_report().lower()
        has_env = sum(1 for e in ["production", "staging", "development", "qa"] if e in c)
        assert has_env >= 3, (
            "should break down systems by environment (prod/staging/dev/qa from MCP)"
        )

    def test_staged_rollout_strategy(self):
        """SKILL Decision Matrix: staging first, then production batches.
        batch_size of 5-10 recommended."""
        c = read_report().lower()
        has_staged = any(t in c for t in [
            "staging first", "test first", "validate first",
            "staged", "phased", "rollout order",
        ])
        has_batch = any(t in c for t in ["batch", "parallel", "rolling"])
        assert has_staged and has_batch, (
            "should recommend staged rollout strategy (SKILL: Decision Matrix)"
        )

    def test_system_tier_classification(self):
        """MCP tags include web-tier, database-tier, app-tier, loadbalancer,
        monitoring, cache-tier. SKILL teaches criticality-based prioritization."""
        c = read_report().lower()
        tiers = sum(1 for t in [
            "web", "database", "app", "load balancer", "loadbalancer",
            "monitoring", "cache",
        ] if t in c)
        assert tiers >= 2, (
            "should classify systems by tier/role from MCP tags"
        )

    def test_high_availability_awareness(self):
        """MCP tags include high-availability and customer-facing.
        SKILL teaches maintenance window for critical systems."""
        c = read_report().lower()
        assert any(t in c for t in [
            "high-availability", "high availability", "ha ",
            "maintenance window", "customer-facing", "customer facing",
        ]), "should recognize HA/customer-facing constraints from MCP tags"

    def test_fleet_size_accuracy(self):
        """MCP has 63 total systems. A skilled agent should report approximate fleet size."""
        c = read_report().lower()
        assert any(t in c for t in [
            "63", "sixty-three", "63 system", "63 host",
            "30 prod", "30 production",
        ]), "should report fleet size or production count from MCP data"
