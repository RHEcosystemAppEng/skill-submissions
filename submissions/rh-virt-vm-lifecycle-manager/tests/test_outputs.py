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
        has_start = "start" in c
        has_explicit_wait = "5" in c and any(
            t in c for t in ["second", "sec", "s wait", "s delay", "s pause"]
        )
        has_sequence = has_stop and has_start
        assert has_sequence and has_explicit_wait, (
            "must decompose restart into stop/wait 5s/start sequence"
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

    def test_resources_get_state_verification(self):
        """Skill teaches using resources_get after vm_lifecycle to verify
        the VM actually transitioned (printableStatus == 'Stopped' or
        'Running'). Without skill, agents assume the action succeeded."""
        c = read_report()
        has_get = "resources_get" in c
        has_verify = any(t in c.lower() for t in [
            "verify", "confirm", "check status", "poll",
        ])
        assert has_get or (has_verify and "printableStatus" in c), (
            "must use resources_get to verify state transition after vm_lifecycle"
        )

    def test_already_in_state_awareness(self):
        """Skill teaches detecting when a VM is already in the desired
        state ('Already Running', 'Already Stopped') and reporting it
        instead of executing a redundant action. Without skill, agents
        blindly issue the command."""
        c = read_report().lower()
        has_already = any(t in c for t in [
            "already running", "already stopped", "already in",
            "desired state", "no action",
        ])
        assert has_already, (
            "must handle already-in-desired-state scenario"
        )

    def test_error_doc_reference(self):
        """Skill references lifecycle-errors.md and scheduling-errors.md
        for troubleshooting stuck transitions and start failures.
        Without skill, agents have no error playbook."""
        c = read_report().lower()
        has_ref = any(t in c for t in [
            "lifecycle-errors", "scheduling-errors",
            "errorunschedulable", "stuck",
        ])
        assert has_ref, (
            "must reference troubleshooting docs for error scenarios"
        )
