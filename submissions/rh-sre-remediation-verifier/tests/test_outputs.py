"""
Tests for rh-sre__remediation-verifier per-skill evaluation.

Skill-specific knowledge tested:
- insights-client --check-results for inventory re-sync
- 24-hour inventory lag caveat
- include_system_profile: true for packages/services
- Defense-in-depth: CVE status + package version + service health
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
        assert any(t in content for t in ["verif", "remediation", "confirm"]), (
            "report should mention key topic"
        )

    def test_report_has_structure(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"


class TestSkillDependent:
    def test_insights_client_check_results(self):
        """Skill: Run 'insights-client --check-results' to trigger inventory
        re-sync so Lightspeed has fresh data. Without skill, agents just
        query the API and get stale data."""
        c = read_report().lower()
        assert any(t in c for t in [
            "insights-client", "check-results",
            "--check-results",
        ]), (
            "should recommend insights-client --check-results for inventory "
            "re-sync (skill: push fresh data to Lightspeed)"
        )

    def test_24h_inventory_lag(self):
        """Skill: Lightspeed inventory updates can take up to 24 hours
        after remediation. Must account for this when interpreting results.
        Without skill, agents expect immediate API updates."""
        c = read_report().lower()
        has_24 = "24" in c
        has_timing = any(t in c for t in [
            "hour", "lag", "delay", "propagat", "stale",
            "not immediately", "may take",
        ])
        assert has_24 and has_timing, (
            "should warn about 24-hour inventory lag "
            "(skill: 'inventory updates may take up to 24 hours')"
        )

    def test_include_system_profile(self):
        """Skill: get_host_details with include_system_profile=true returns
        installed_packages and enabled_services for deep verification.
        Without skill, agents don't request the system profile."""
        c = read_report().lower()
        assert any(t in c for t in [
            "include_system_profile", "system_profile",
            "system profile", "installed_packages",
        ]), (
            "should use include_system_profile for package/service data "
            "(skill: required parameter for deep checks)"
        )

    def test_defense_in_depth_verification(self):
        """Skill: Three verification layers: CVE status (still vulnerable?),
        package version (updated?), service health (running?). At least 2
        must be present."""
        c = read_report().lower()
        has_cve = any(t in c for t in ["cve", "vulnerab", "affected"])
        has_pkg = any(t in c for t in ["package", "version", "installed", "fixed"])
        has_svc = any(t in c for t in ["service", "running", "health", "enabled"])
        checks = sum([has_cve, has_pkg, has_svc])
        assert checks >= 2, (
            f"should verify at least 2 of 3: CVE status, package version, "
            f"service health (found {checks}; skill: defense in depth)"
        )

    def test_per_system_results(self):
        """Skill: Report per-system verification results (pass/fail per host),
        not just an aggregate summary."""
        c = read_report().lower()
        has_per_system = any(t in c for t in [
            "per system", "per-system", "each system", "each host",
            "per host", "system-by-system",
        ])
        has_pass_fail = any(t in c for t in [
            "pass", "fail", "success", "remediated", "verified",
        ])
        assert has_per_system and has_pass_fail, (
            "should provide per-system verification results "
            "(skill: per-system checks with pass/fail status)"
        )
