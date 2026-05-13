"""
Tests for rh-basic-red-hat-support-severity per-skill evaluation.

Only differentiating tests kept — dead-weight tests where both
control and treatment pass 3/3 have been removed.
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
    def test_sla_response_times_premium(self):
        """Skill teaches exact Premium SLA response times (1 hour for Sev 1,
        2 hours for Sev 2). Without skill, agents give approximate values."""
        c = read_report()
        assert "1 hour" in c.lower() or "1h" in c.lower(), (
            "must state exact Sev 1 Premium SLA: 1 hour"
        )

    def test_sla_response_times_standard(self):
        """Skill teaches Standard SLA times differ from Premium
        (1 business hour vs 4 business hours for Sev 2)."""
        c = read_report()
        has_bh = "business hour" in c.lower() or "business day" in c.lower()
        assert has_bh, (
            "must distinguish business hours in Standard SLA"
        )

    def test_24x7_coverage_guidance(self):
        """Skill teaches Sev 2 requires explicitly requesting 24x7
        coverage when filing. Without skill, agents don't know this."""
        c = read_report()
        assert "24x7" in c or "24/7" in c, (
            "must address 24x7 coverage availability"
        )

    def test_phone_call_filing_tip(self):
        """Skill teaches filing tip: for Sev 1/2, submit online then
        immediately call the support number. Without skill, agents
        give generic filing advice."""
        c = read_report()
        assert "call" in c.lower() or "phone" in c.lower(), (
            "must recommend phone follow-up for high severity tickets"
        )

    def test_cve_severity_adjustment(self):
        """Skill teaches CVE severity adjustment rule: Critical/Important
        CVE on unpatched production → Sev 2 not Sev 3. Without skill,
        agents don't apply this specific adjustment."""
        c = read_report()
        has_cve_sev = "sev 2" in c.lower() or "severity 2" in c.lower()
        has_critical = "critical" in c.lower() or "important" in c.lower()
        assert has_cve_sev and has_critical, (
            "must apply CVE severity adjustment to ticket recommendation"
        )
