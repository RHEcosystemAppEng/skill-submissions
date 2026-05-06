"""
Tests for rh-sre__remediation per-skill evaluation.

Exact-field tests: require API field names and anti-patterns that only SKILL.md teaches.
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

    def test_mentions_cve(self):
        content = read_report()
        assert "CVE" in content

    def test_report_has_structure(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"


class TestSkillDependent:
    def test_advisory_available_field(self):
        """Skill teaches using advisory_available (not rules[]) to
        determine remediatability. Without skill, agents check rules[]
        which can be empty even when remediation exists."""
        c = read_report()
        assert "advisory_available" in c, (
            "must reference advisory_available field for remediatability"
        )

    def test_not_rules_array(self):
        """Skill teaches that rules[] emptiness does NOT mean no remediation.
        Without skill, agents use rules[] as the source of truth."""
        c = read_report().lower()
        if "rules" in c:
            has_advisory = "advisory_available" in read_report()
            assert has_advisory, (
                "if mentioning rules[], must also reference advisory_available "
                "as the correct remediatability check"
            )

    def test_remediation_available_gate(self):
        """Skill teaches remediation_available: true or validation_status:
        'valid' as the gate to proceed. Without skill, agents proceed
        without validation."""
        c = read_report()
        has_gate = "remediation_available" in c or "validation_status" in c
        assert has_gate, (
            "must reference remediation_available or validation_status gate"
        )

    def test_advisories_list_field(self):
        """Skill teaches using advisories_list for remediation details.
        Without skill, agents don't know this field exists."""
        c = read_report()
        assert "advisories_list" in c or "advisories" in c.lower(), (
            "must reference advisories_list field"
        )

    def test_absolute_playbook_path(self):
        """Skill teaches playbook files must use absolute paths for the
        repo location. Without skill, agents use relative paths."""
        c = read_report()
        has_playbook = "playbook" in c.lower()
        has_path = "/" in c and "playbooks/" in c
        assert has_playbook and has_path, (
            "must specify playbook with absolute repo path"
        )
