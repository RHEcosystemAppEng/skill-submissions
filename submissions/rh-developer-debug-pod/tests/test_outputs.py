"""
Tests for rh-developer-debug-pod per-skill evaluation.

Only differentiating tests kept — dead-weight tests where both
control and treatment pass have been removed.
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
    def test_pod_name_from_cluster(self):
        """Skill-equipped agents use pod_list MCP tool to discover the
        actual pod name. Without skill, agents write generic pod
        debugging guides without specific pod identifiers."""
        c = read_report()
        assert "web-frontend-6c5d8b7a9" in c or "p4n2j" in c or (
            "web-frontend" in c.lower() and "6c5d8b" in c
        ), "must reference the actual pod name from cluster"

    def test_memory_limit_64mi(self):
        """Skill-equipped agents discover the specific memory limit (64Mi)
        via resources_get MCP tool. Without skill, agents mention
        resource limits generically without the actual value."""
        c = read_report()
        assert "64Mi" in c or "64 Mi" in c or "64m" in c.lower(), (
            "must reference the specific memory limit 64Mi from cluster"
        )

    def test_port_3000_from_logs(self):
        """Skill-equipped agents discover port 3000 from container logs
        via pod_logs MCP tool. Without skill, agents assume standard
        port 8080 without reading actual logs."""
        c = read_report()
        assert "3000" in c, (
            "must reference port 3000 discovered from container logs"
        )

    def test_restart_count_from_cluster(self):
        """Skill-equipped agents report the actual restart count from
        the cluster. Without skill, agents describe CrashLoopBackOff
        without specific restart data."""
        c = read_report()
        assert "8" in c and ("restart" in c.lower() or "crash" in c.lower()), (
            "must report the specific restart count from cluster"
        )

    def test_oc_set_resources_remediation(self):
        """Skill teaches concrete remediation using oc set resources
        or oc patch to increase memory limits. Without skill, agents
        give vague 'increase limits' advice."""
        c = read_report()
        assert "oc set resources" in c or "oc patch" in c or (
            "set resources" in c.lower()
        ), "must include concrete oc remediation command"

    def test_debug_network_escalation(self):
        """Skill teaches escalating to /debug-network or /debug-build
        when the issue is not resource-related. Without skill, agents
        don't know the debugging skill chain."""
        c = read_report().lower()
        assert "debug-network" in c or "debug-build" in c or (
            "network" in c and "debug" in c
        ), "must reference debug-network or debug-build escalation"
