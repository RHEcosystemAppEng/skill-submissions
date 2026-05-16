"""
Tests for rh-automation-resolution-advisor per-skill evaluation.

Only differentiating tests kept — dead-weight tests where both
control and treatment pass have been removed.
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
    def test_error_classification_doc(self):
        """Skill teaches consulting error-classification.md for the
        resolution owner mapping table. Without skill, agents provide
        resolutions without structured classification."""
        c = read_report().lower()
        assert "error-classification" in c, (
            "must reference error-classification.md document"
        )

    def test_job_troubleshooting_doc(self):
        """Skill teaches consulting job-troubleshooting.md as a second
        required reference. Without skill, agents skip dual-doc
        consultation."""
        c = read_report().lower()
        assert "job-troubleshooting" in c, (
            "must reference job-troubleshooting.md document"
        )

    def test_resolution_owner_taxonomy(self):
        """Skill teaches the resolution owner taxonomy: Network/Infra,
        Platform Admin, Playbook Developer, Ops Team. Without skill,
        agents assign resolutions without ownership classification."""
        c = read_report().lower()
        owners = [
            "platform admin", "playbook developer",
            "network", "infra", "ops team",
        ]
        found = sum(1 for o in owners if o in c)
        assert found >= 1, (
            "must classify resolution owner (Platform Admin, "
            "Playbook Developer, Network/Infra, Ops Team)"
        )

    def test_governance_readiness_gap(self):
        """Skill teaches identifying related governance gaps and linking
        to governance-readiness.md domains. Without skill, agents
        provide fixes without governance context."""
        c = read_report().lower()
        assert "governance" in c and ("gap" in c or "readiness" in c or "domain" in c), (
            "must identify related governance gaps"
        )

    def test_execution_summary_next_step(self):
        """Skill teaches routing to execution-summary as the final
        step in the forensic pipeline. Without skill, agents don't
        know the skill chain."""
        c = read_report().lower()
        assert "execution-summary" in c or "execution summary" in c, (
            "must reference execution-summary as pipeline next step"
        )

    def test_aap_doc_chapter_references(self):
        """Skill teaches citing specific AAP documentation chapters
        (e.g., Ch. 15 Security Best Practices, Ch. 17 Instance Groups).
        Without skill, agents give generic 'consult docs' advice."""
        c = read_report()
        assert "Ch." in c or "Chapter" in c or "Sec." in c or "Section" in c, (
            "must cite specific AAP documentation chapters/sections"
        )
