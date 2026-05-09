"""
Tests for rh-virt__vm-snapshot-list per-skill evaluation.

Dead-weight and same-rate tests removed. Only differentiating tests kept.
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
    def test_ready_to_use_field(self):
        """Skill teaches status.readyToUse as the field that indicates
        whether a snapshot can be used for restore. Without skill,
        agents only check status.phase."""
        c = read_report()
        assert "readyToUse" in c, (
            "must reference status.readyToUse field"
        )

    def test_status_phase_values(self):
        """Skill teaches exact status.phase values: InProgress, Succeeded,
        Failed. Without skill, agents use generic status descriptions."""
        c = read_report()
        for phase in ["InProgress", "Succeeded", "Failed"]:
            assert phase in c, (
                f"must reference exact phase value: {phase}"
            )

    def test_ready_to_use_false_troubleshooting(self):
        """Skill teaches that readyToUse == false is the trigger for
        troubleshooting. Generic 'conditions' appears everywhere."""
        c = read_report()
        has_ready_false = (
            "readyToUse" in c
            and ("false" in c.lower() or "not ready" in c.lower())
        )
        assert has_ready_false, (
            "must reference readyToUse == false as troubleshooting trigger"
        )
