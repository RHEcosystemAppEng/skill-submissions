"""
Tests for rh-basic__red-hat-support-severity evaluation.
Baseline tests: any competent agent should pass.
Skill-dependent tests: require knowledge from SKILL.md.
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

    def test_mentions_severity(self):
        c = read_report().lower()
        assert any(t in c for t in ["severity", "sev 1", "sev 2", "sev1", "sev2"]), (
            "report should mention support ticket severity"
        )

    def test_report_has_structure(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"


class TestSkillDependent:
    def test_cve_adjustment_rule(self):
        """SKILL CVE adjustment: Critical CVE on unpatched production that is
        NOT fully down -> Sev 2, not Sev 3. Without skill, agents rate a
        running server with a CVE as Sev 3 (partial loss / workaround)."""
        c = read_report().lower()
        has_scenario_b = "cve-2024-6387" in c or "regresshion" in c
        has_sev2 = "sev 2" in c or "severity 2" in c or "sev2" in c or "high" in c
        assert has_scenario_b and has_sev2, (
            "should recommend Sev 2 for unpatched Critical CVE on running production "
            "(SKILL CVE adjustment rule)"
        )

    def test_sla_premium_vs_standard(self):
        """SKILL SLA reference: Premium 1hr for Sev 1, Standard 1 business hour.
        Without skill, agents give vague SLA guidance."""
        c = read_report().lower()
        has_premium = "premium" in c
        has_standard = "standard" in c
        has_hours = any(t in c for t in ["1 hour", "2 hour", "4 hour", "1 business"])
        assert has_premium and has_standard and has_hours, (
            "should show SLA response times for Premium and Standard tiers"
        )

    def test_filing_tip_call(self):
        """SKILL output: Sev 1/2 filing tip is 'Submit online, then immediately
        call'. Without skill, agents just say 'file a ticket'."""
        c = read_report().lower()
        assert any(t in c for t in [
            "call", "phone",
        ]) and any(t in c for t in [
            "sev 1", "sev 2", "severity 1", "severity 2", "critical", "high",
        ]), "should include filing tip to call for Sev 1/2 tickets"

    def test_diagnostics_recommendation(self):
        """SKILL output: recommends '/red-hat-diagnostics' for diagnostic data
        or mentions attaching diagnostics. Without skill, agents skip this."""
        c = read_report().lower()
        assert any(t in c for t in [
            "diagnostic", "sos report", "must-gather",
            "red-hat-diagnostics",
        ]), "should recommend gathering diagnostics for the support ticket"

    def test_24x7_coverage(self):
        """SKILL SLA: Premium Sev 1 = 24x7, Sev 2 = must explicitly request.
        Without skill, agents don't distinguish 24x7 availability."""
        c = read_report().lower()
        assert "24x7" in c or "24/7" in c or "around the clock" in c, (
            "should mention 24x7 coverage availability for high-severity tickets"
        )

    def test_business_impact_statement(self):
        """SKILL output: ticket should include 'clear business impact statement'.
        Without skill, agents list generic ticket fields."""
        c = read_report().lower()
        assert "business impact" in c or "impact statement" in c, (
            "should advise including a business impact statement in the ticket"
        )
