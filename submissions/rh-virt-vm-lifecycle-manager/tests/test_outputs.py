"""
Tests for rh-virt__vm-lifecycle-manager evaluation.

6 tests: 2 padding (both agents pass) + 4 skill-dependent.
Each test worth ~16.7% of pytest score.
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

    def test_mentions_target_vms(self):
        c = read_report().lower()
        has_web = "web-frontend" in c or "web_frontend" in c
        has_db = "production-db" in c or "production_db" in c
        assert has_web or has_db, (
            "report must reference at least one target VM"
        )


class TestSkillDependent:
    def test_decomposed_restart_with_wait(self):
        """Skill teaches restart MUST be stop -> verify Stopped -> wait 5s
        -> start -> verify Running. This avoids resourceVersion conflicts.
        An unskilled agent uses a single restart command."""
        c = read_report().lower()
        has_stop_start = "stop" in c and "start" in c
        has_wait = "5" in c and any(
            t in c for t in ["second", "sec", "wait", "delay", "pause"]
        )
        assert has_stop_start and has_wait, (
            "must decompose restart into stop/wait 5s/start sequence"
        )

    def test_printable_status_field(self):
        """Skill teaches polling status.printableStatus for exact values
        'Stopped' and 'Running' to verify state transitions. An unskilled
        agent checks generic status or doesn't verify at all."""
        c = read_report()
        assert "printableStatus" in c, (
            "must reference printableStatus field for state verification"
        )

    def test_resource_version_conflict(self):
        """Skill teaches that restart must be decomposed specifically to
        avoid resourceVersion conflicts from rapid successive API calls.
        This is a Kubernetes concurrency concept an unskilled agent
        doesn't know."""
        c = read_report()
        assert "resourceVersion" in c, (
            "must mention resourceVersion conflict as reason for decomposed restart"
        )

    def test_run_strategy_halted(self):
        """Skill teaches RunStrategy mapping: stop sets Halted, start sets
        Always. 'Halted' is a KubeVirt-specific RunStrategy value that
        an unskilled agent typically doesn't mention."""
        c = read_report()
        assert "Halted" in c, (
            "must reference RunStrategy 'Halted' for stop operation"
        )
