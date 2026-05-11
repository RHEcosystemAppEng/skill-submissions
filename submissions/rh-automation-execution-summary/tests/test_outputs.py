"""Execution summary tests - audit trail, MCP tools, decisions."""
import os, pytest

REPORT = "/solution/report.md"

def read_report():
    if not os.path.exists(REPORT):
        pytest.fail(f"Required file not found: {REPORT}")
    with open(REPORT) as f:
        return f.read()

class TestBaseline:
    def test_report_exists(self):
        assert os.path.exists(REPORT)
    def test_report_has_content(self):
        assert len(read_report()) > 400

class TestAuditSections:
    """The execution summary format is defined in the skill."""
    def test_workflow_overview(self):
        c = read_report().lower()
        assert "workflow" in c or "overview" in c
    def test_documents_consulted(self):
        c = read_report().lower()
        assert "document" in c or "consulted" in c or "reference" in c
    def test_mcp_tools_section(self):
        c = read_report().lower()
        assert "mcp" in c and "tool" in c
    def test_decisions_section(self):
        c = read_report().lower()
        assert "decision" in c
    def test_outcomes_section(self):
        c = read_report().lower()
        assert "outcome" in c or "result" in c
    def test_recommendations(self):
        c = read_report().lower()
        assert "recommend" in c or "follow-up" in c or "improvement" in c
