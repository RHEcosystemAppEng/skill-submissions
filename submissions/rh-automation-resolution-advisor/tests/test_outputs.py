"""
Tests for rh-automation-resolution-advisor per-skill evaluation.

Skill provides Red Hat documentation-backed resolution recommendations.
Teaches error classification taxonomy, resolution owner mapping, and
specific AAP documentation chapter references.
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
        resolution owner mapping table."""
        c = read_report().lower()
        assert "error-classification" in c, (
            "must reference error-classification.md document"
        )

    def test_job_troubleshooting_doc(self):
        """Skill teaches consulting job-troubleshooting.md as the
        second required reference document."""
        c = read_report().lower()
        assert "job-troubleshooting" in c, (
            "must reference job-troubleshooting.md document"
        )

    def test_resolution_owner_taxonomy(self):
        """Skill teaches the resolution owner taxonomy with specific
        roles: Platform Admin, Playbook Developer, Ops Team, Network/Infra."""
        c = read_report().lower()
        owners = [
            "platform admin", "playbook developer", "ops team",
            "network", "infra",
        ]
        found = sum(1 for o in owners if o in c)
        assert found >= 2, (
            f"must classify resolution owners (Platform Admin, Playbook Developer, "
            f"Ops Team, Network/Infra); found {found}"
        )

    def test_error_classification_categories(self):
        """Skill teaches 3 error classifications: Platform, Code, Config.
        Without skill, agents don't use this taxonomy."""
        c = read_report()
        categories = ["Platform", "Code", "Config"]
        found = sum(1 for cat in categories if cat in c)
        assert found >= 2, (
            f"must use error classification categories "
            f"(Platform/Code/Config); found {found}/3"
        )

    def test_aap_doc_references(self):
        """Skill teaches citing specific AAP documents (AAP 2.6 Troubleshooting
        Guide, AAP 2.5 Instance Groups, EE Guide). Without skill,
        agents give generic 'consult docs' advice."""
        c = read_report()
        refs = [
            "AAP 2.6", "AAP 2.5", "Troubleshooting Guide",
            "EE Guide", "Instance Group", "Security Best Practices",
        ]
        found = sum(1 for r in refs if r in c)
        assert found >= 2, (
            f"must cite specific AAP documentation references; found {found}"
        )

    def test_execution_summary_next_step(self):
        """Skill teaches routing to execution-summary as the final
        step in the forensic pipeline."""
        c = read_report().lower()
        assert "execution-summary" in c or "execution summary" in c, (
            "must reference execution-summary as pipeline next step"
        )
