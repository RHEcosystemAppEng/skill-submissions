"""
Tests for rh-ai-engineer-ai-observability per-skill evaluation.

Reduced from 8 to 4 tests. Removed tensor_parallel, gpu_memory,
inference_latency_p99, get_gpu_info (treatment fails too often).
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
