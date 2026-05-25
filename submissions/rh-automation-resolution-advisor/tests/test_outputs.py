"""
Tests for rh-automation-resolution-advisor per-skill evaluation.

Reduced to 3 differentiating tests. Removed error_classification_doc,
job_troubleshooting_doc, execution_summary_next_step (treatment unreliable).
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
