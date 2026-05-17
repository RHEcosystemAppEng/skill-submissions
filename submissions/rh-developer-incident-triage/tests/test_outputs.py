"""
Tests for rh-developer-incident-triage per-skill evaluation.

Kept tests that differentiate treatment from control per trial logs.
Removed checks both variants pass at 100% (five whys, guardrails, due diligence).
"""
import os
import re
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
    def test_confidence_score(self):
        """Skill requires numeric confidence (0.XX). Control often omits this."""
        c = read_report().lower()
        assert re.search(r'confidence[\s:]*[01]\.\d', c), (
            "must include numeric confidence score"
        )
