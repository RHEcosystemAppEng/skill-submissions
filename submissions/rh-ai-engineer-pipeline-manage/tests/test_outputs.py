"""Pipeline manage skill tests - DSPA, KFP 2.0, scheduling."""
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

class TestDSPA:
    """DSPA (DataSciencePipelinesApplication) is RHOAI-specific."""
    def test_dspa_mentioned(self):
        c = read_report().lower()
        assert "dspa" in c or "datasciencepipelinesapplication" in c or "pipeline server" in c
    def test_kubeflow_pipelines(self):
        c = read_report().lower()
        assert "kubeflow" in c or "kfp" in c or "data science pipeline" in c

class TestPipelineRun:
    """Pipeline run submission and monitoring."""
    def test_pipeline_run(self):
        c = read_report().lower()
        assert "pipelinerun" in c or "pipeline run" in c
    def test_yaml_definition(self):
        c = read_report().lower()
        assert "yaml" in c or "definition" in c
    def test_step_level_monitoring(self):
        c = read_report().lower()
        assert "step" in c and ("log" in c or "status" in c or "progress" in c)

class TestScheduling:
    """Scheduled/recurring runs use ScheduledWorkflow CR or cron."""
    def test_scheduling(self):
        c = read_report().lower()
        assert "schedul" in c or "recurring" in c or "cron" in c
    def test_cron_expression(self):
        c = read_report()
        assert re.search(r'\d+\s+\d+\s+\*', c) or "cron" in c.lower()

class TestLifecycle:
    """Pipeline lifecycle management."""
    def test_delete_warning(self):
        c = read_report().lower()
        assert "delet" in c and ("warn" in c or "confirm" in c or "caution" in c)
