"""Guardrails config skill tests - TrustyAI orchestrator, detectors, CRD."""
import os, re, pytest

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

class TestGuardrailsOrchestrator:
    """GuardrailsOrchestrator CRD is unique to TrustyAI/RHOAI 2.14+."""
    def test_mentions_guardrails_orchestrator(self):
        c = read_report().lower()
        assert "guardrailsorchestrator" in c or "guardrails orchestrator" in c
    def test_mentions_trustyai(self):
        c = read_report().lower()
        assert "trustyai" in c
    def test_mentions_crd_check(self):
        c = read_report().lower()
        assert "crd" in c or "customresourcedefinition" in c

class TestDetectorConfiguration:
    """Specific detector types from the skill."""
    def test_content_safety_detector(self):
        c = read_report().lower()
        assert "content safety" in c or "granite-guardian" in c or "granite guardian" in c
    def test_pii_detection(self):
        c = read_report().lower()
        assert "pii" in c
    def test_prompt_injection(self):
        c = read_report().lower()
        assert "prompt injection" in c or "injection" in c
    def test_detector_model_reference(self):
        c = read_report().lower()
        assert "granite-guardian" in c or "granite guardian" in c or "ibm-granite" in c
    def test_detection_policy(self):
        c = read_report().lower()
        assert "block" in c or "warn" in c or "passthrough" in c

class TestConfigMap:
    """Skill requires creating a detector ConfigMap."""
    def test_configmap_mentioned(self):
        c = read_report().lower()
        assert "configmap" in c
    def test_input_output_scope(self):
        c = read_report().lower()
        assert ("input" in c and "output" in c) or "both" in c

class TestGuardedEndpoint:
    """Guarded endpoint is different from original - skill-specific knowledge."""
    def test_guarded_endpoint_distinct(self):
        c = read_report().lower()
        assert "guarded endpoint" in c or "guarded" in c
    def test_safe_and_unsafe_testing(self):
        c = read_report().lower()
        has_safe = "safe" in c or "normal" in c or "legitimate" in c
        has_unsafe = "unsafe" in c or "injection" in c or "blocked" in c
        assert has_safe and has_unsafe
