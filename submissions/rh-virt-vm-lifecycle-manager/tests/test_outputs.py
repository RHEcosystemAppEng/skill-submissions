"""
Tests for rh-virt__vm-lifecycle-manager per-skill evaluation.

Exact-field tests: require procedure details that only SKILL.md teaches.
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

    def test_mentions_operations(self):
        content = read_report().lower()
        assert "stop" in content or "start" in content or "restart" in content

    def test_report_has_structure(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"


class TestSkillDependent:
    def test_decomposed_restart(self):
        """Skill teaches restart must be decomposed into stop -> verify
        Stopped -> wait 5s -> start -> verify Running. NOT a single
        atomic restart call. Without skill, agents use one restart command."""
        c = read_report().lower()
        has_stop = "stop" in c
        has_wait = any(t in c for t in ["wait", "5 second", "delay", "pause"])
        has_start = "start" in c
        has_sequence = has_stop and has_start
        assert has_sequence and has_wait, (
            "must decompose restart into stop/wait/start sequence"
        )

    def test_printable_status_polling(self):
        """Skill teaches polling status.printableStatus for 'Stopped'
        before proceeding to start. Without skill, agents don't verify
        the intermediate state."""
        c = read_report()
        assert "printableStatus" in c, (
            "must poll printableStatus to verify Stopped/Running state"
        )

    def test_resource_version_conflict(self):
        """Skill teaches that restart must decompose to avoid
        resourceVersion conflicts. Without skill, agents don't know
        about this Kubernetes concurrency issue."""
        c = read_report()
        assert "resourceVersion" in c, (
            "must mention resourceVersion conflict avoidance as reason for decomposed restart"
        )

    def test_run_strategy_mapping(self):
        """Skill teaches RunStrategy outcomes: start->Always, stop->Halted,
        restart->Always. Without skill, agents don't know the mapping."""
        c = read_report()
        has_halted = "Halted" in c
        has_always = "Always" in c
        assert has_halted and has_always, (
            "must reference RunStrategy values: Halted (stop) and Always (start/restart)"
        )

    def test_vm_lifecycle_tool(self):
        """Skill teaches using vm_lifecycle MCP tool with action parameter.
        Without skill, agents use generic kubectl commands."""
        c = read_report()
        assert "vm_lifecycle" in c, (
            "must reference vm_lifecycle tool for operations"
        )
