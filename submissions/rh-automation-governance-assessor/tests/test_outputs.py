"""
Tests for rh-automation-governance-assessor per-skill evaluation.

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
    def test_governance_readiness_assessor_invocation(self):
        """Skill teaches invoking governance-readiness-assessor sub-skill
        for the 7-domain assessment. Without skill, agents do freeform audit."""
        c = read_report()
        assert "governance-readiness-assessor" in c or "readiness-assessor" in c, (
            "must reference governance-readiness-assessor sub-skill"
        )

    def test_aap_mcp_validator_invocation(self):
        """Skill teaches invoking aap-mcp-validator as first step
        before any assessment queries."""
        c = read_report()
        assert "aap-mcp-validator" in c or "mcp-validator" in c, (
            "must reference aap-mcp-validator sub-skill invocation"
        )

    def test_governance_readiness_doc(self):
        """Skill teaches consulting governance-readiness.md for the
        7-domain assessment framework with Red Hat citations."""
        c = read_report()
        assert "governance-readiness" in c, (
            "must reference governance-readiness.md"
        )
