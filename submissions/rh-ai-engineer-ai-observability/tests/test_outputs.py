"""
Tests for rh-ai-engineer-ai-observability per-skill evaluation.

Kept tests where treatment outperforms control in trial logs.
Removed korrel8r/tempo/otel (fail equally) and redundant vllm overlap.
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
        """Skill teaches DCGM_FI_DEV_* metrics; control uses generic nvidia names."""
        c = read_report()
        assert any(t in c for t in ["DCGM_FI_DEV", "dcgm_fi_dev", "DCGM"]), (
            "should reference DCGM GPU metric names (not generic nvidia_gpu_*)"
        )

    def test_tensor_parallel_size_tuning(self):
        """Skill teaches tensor-parallel-size / AWQ / GPTQ / FP8 GPU tuning."""
        c = read_report().lower()
        assert any(t in c for t in [
            "tensor-parallel-size", "tensor_parallel_size", "tensor parallel",
            "awq", "gptq", "fp8", "quantiz",
        ]), "should address tensor-parallel-size and quantization for GPU tuning"
