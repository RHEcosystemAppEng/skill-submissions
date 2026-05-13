"""
Tests for rh-automation-execution-summary per-skill evaluation.

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
    def test_documents_consulted_section(self):
        """Skill teaches a specific 'Documents Consulted' section with
        document name, topic, and Red Hat citation columns. Without skill,
        agents write freeform summaries."""
        c = read_report()
        assert "Documents Consulted" in c, (
            "must include structured Documents Consulted section"
        )

    def test_mcp_tools_used_section(self):
        """Skill teaches a structured 'MCP Tools Used' table with
        Server, Tool, Purpose, Result columns."""
        c = read_report()
        assert "MCP Tools Used" in c or "MCP Tools Invoked" in c, (
            "must include structured MCP Tools Used section"
        )

    def test_governance_decisions_section(self):
        """Skill teaches a 'Governance Decisions' section tracking
        each decision with its documentary basis and outcome."""
        c = read_report()
        assert "Governance Decisions" in c or "Decisions Made" in c, (
            "must include structured Governance Decisions section"
        )

    def test_audit_note_traceability(self):
        """Skill teaches including an audit note confirming all decisions
        are traceable to Red Hat documentation citations."""
        c = read_report()
        assert "Audit Note" in c or "traceable" in c.lower(), (
            "must include audit traceability note"
        )

    def test_red_hat_documentation_citations(self):
        """Skill teaches citing specific Red Hat AAP chapters
        (e.g., Ch. 9, Ch. 15, Ch. 25) as decision basis."""
        c = read_report()
        assert "Ch." in c or "Chapter" in c or "Red Hat AAP" in c, (
            "must cite Red Hat documentation chapters"
        )
