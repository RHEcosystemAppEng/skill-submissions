"""Model registry skill tests - RegisteredModel, ModelVersion, ModelArtifact."""
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

class TestModelRegistryConcepts:
    """RegisteredModel, ModelVersion, ModelArtifact are RHOAI-specific CRs."""
    def test_registered_model(self):
        c = read_report().lower()
        assert "registeredmodel" in c or "registered model" in c
    def test_model_version(self):
        c = read_report().lower()
        assert "modelversion" in c or "model version" in c or "v2.1" in c
    def test_model_artifact(self):
        c = read_report().lower()
        assert "modelartifact" in c or "model artifact" in c or "artifact" in c
    def test_storage_uri(self):
        c = read_report().lower()
        assert "storage" in c and ("uri" in c or "s3" in c)

class TestPromotion:
    """Cross-environment promotion is skill-specific workflow."""
    def test_promotion_mentioned(self):
        c = read_report().lower()
        assert "promot" in c
    def test_environments(self):
        c = read_report().lower()
        envs = sum(1 for e in ["dev", "staging", "prod"] if e in c)
        assert envs >= 2, "Must reference at least 2 environments"
    def test_data_connection(self):
        c = read_report().lower()
        assert "data connection" in c or "data science project" in c or "s3" in c

class TestModelCatalog:
    """Model Catalog is distinct from Registry in RHOAI."""
    def test_registry_vs_catalog(self):
        c = read_report().lower()
        assert "registry" in c
