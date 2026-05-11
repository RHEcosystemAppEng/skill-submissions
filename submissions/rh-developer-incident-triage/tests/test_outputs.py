"""Incident triage skill tests - Five Whys, guardrails, due diligence."""
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
        assert os.path.exists(REPORT)

    def test_report_has_content(self):
        assert len(read_report()) > 500

class TestFiveWhysMethodology:
    """Five Whys is the core differentiation - unskilled agents won't structure this way."""
    def test_five_whys_present(self):
        c = read_report().lower()
        assert "five whys" in c or "5 whys" in c or "causal chain" in c, \
            "Must use Five Whys methodology"

    def test_multiple_why_levels(self):
        c = read_report().lower()
        why_count = len(re.findall(r'why[\s\?#\d]', c))
        assert why_count >= 3, "Must trace at least 3 levels of 'why'"

    def test_root_cause_identified(self):
        c = read_report().lower()
        assert "root cause" in c, "Must identify root cause"

class TestInvestigationGuardrails:
    """Guardrails are skill-specific knowledge."""
    def test_exhaustive_verification(self):
        c = read_report().lower()
        assert "exhaustive" in c or "all resources" in c or "ownership chain" in c

    def test_contradicting_evidence(self):
        c = read_report().lower()
        assert "contradict" in c or "alternative" in c or "ruled out" in c

    def test_evidence_based(self):
        c = read_report().lower()
        assert "evidence" in c

    def test_error_separation(self):
        c = read_report().lower()
        assert "investigation" in c and ("error" in c or "limitation" in c)

class TestAdversarialDueDiligence:
    """8-dimension due diligence review is unique to this skill."""
    def test_confidence_score(self):
        c = read_report().lower()
        assert re.search(r'confidence[\s:]*[01]\.\d', c), \
            "Must include numeric confidence score (0.XX format)"

    def test_due_diligence_dimensions(self):
        c = read_report().lower()
        dimensions = ["causal completeness", "target accuracy", "evidence sufficiency",
                      "alternative hypothes", "scope completeness", "proportionality",
                      "regression", "confidence calibration"]
        found = sum(1 for d in dimensions if d in c)
        assert found >= 4, f"Must address at least 4 of 8 due diligence dimensions, found {found}"

class TestRemediationTarget:
    """Skill requires distinguishing symptom reporter from misconfigured resource."""
    def test_remediation_target_specified(self):
        c = read_report().lower()
        assert "remediation" in c and "target" in c

    def test_signal_classification(self):
        c = read_report().lower()
        assert "severity" in c or "classification" in c or "critical" in c or "high" in c

class TestHierarchicalInvestigation:
    """Skill requires tracing Deployment -> ReplicaSet -> Pod -> Container."""
    def test_ownership_chain(self):
        c = read_report().lower()
        chain_terms = ["deployment", "replicaset", "pod"]
        found = sum(1 for t in chain_terms if t in c)
        assert found >= 2, "Must trace ownership chain (Deployment/ReplicaSet/Pod)"

    def test_uses_events(self):
        c = read_report().lower()
        assert "event" in c, "Must analyze Kubernetes events"

    def test_uses_logs(self):
        c = read_report().lower()
        assert "log" in c, "Must analyze container logs"
