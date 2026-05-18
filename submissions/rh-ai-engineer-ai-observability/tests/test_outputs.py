"""
Tests for rh-ai-engineer-ai-observability per-skill evaluation.

Skill teaches querying AI model inference metrics, GPU utilization,
and distributed traces on OpenShift AI. Mock has ml-production namespace
with text-gen-legacy (OOMKilled, 22GB/24GB GPU, p99=2800ms) and
sentiment-classifier (healthy, 4GB/24GB).
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
    def test_dcgm_gpu_metric_names(self):
        """Skill teaches DCGM_FI_DEV_* metrics for GPU monitoring.
        Without skill, agents use generic nvidia names."""
        c = read_report()
        assert any(t in c for t in ["DCGM_FI_DEV", "dcgm_fi_dev", "DCGM"]), (
            "should reference DCGM GPU metric names"
        )

    def test_tensor_parallel_size_tuning(self):
        """Skill teaches tensor-parallel-size / quantization (AWQ/GPTQ/FP8)."""
        c = read_report().lower()
        assert any(t in c for t in [
            "tensor-parallel-size", "tensor_parallel_size", "tensor parallel",
            "awq", "gptq", "fp8", "quantiz",
        ]), "should address tensor-parallel-size or quantization for GPU tuning"

    def test_analyze_vllm_tool(self):
        """Skill teaches using analyze_vllm MCP tool for model performance.
        Without skill, agents describe generic kubectl commands."""
        c = read_report()
        assert "analyze_vllm" in c or "chat_vllm" in c, (
            "must reference analyze_vllm or chat_vllm MCP tools"
        )

    def test_text_gen_legacy_model(self):
        """Mock has text-gen-legacy model that is OOMKilled with 22GB/24GB GPU.
        Skilled agent discovers this from MCP data."""
        c = read_report().lower()
        assert "text-gen-legacy" in c, (
            "must reference text-gen-legacy model from mock cluster"
        )

    def test_gpu_memory_utilization(self):
        """Mock shows 22GB/24GB GPU memory (91.7% utilization) for
        text-gen-legacy. Skilled agent reports specific values."""
        c = read_report()
        assert any(t in c for t in ["22", "24", "91", "gpu_memory"]), (
            "must report GPU memory utilization values from mock data"
        )

    def test_inference_latency_p99(self):
        """Mock shows p99 latency of 2800ms for text-gen-legacy.
        Skilled agent surfaces this from metrics."""
        c = read_report()
        assert "2800" in c or "p99" in c.lower(), (
            "must report p99 inference latency from mock metrics"
        )

    def test_get_gpu_info_tool(self):
        """Skill teaches using get_gpu_info MCP tool for GPU inventory."""
        c = read_report()
        assert any(t in c for t in [
            "get_gpu_info", "get_deployment_info",
            "list_models", "list_vllm_namespaces",
        ]), "must reference observability MCP tools (get_gpu_info, list_models)"
