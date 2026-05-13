"""
Tests for rh-developer-debug-rhel per-skill evaluation.

Only differentiating tests kept — dead-weight tests where both
control and treatment pass 3/3 have been removed.
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
    def test_semanage_port_type(self):
        """Skill teaches 'semanage port -a -t http_port_t -p tcp [port]'
        as the specific SELinux fix for port binding denials. Without skill,
        agents give generic semanage advice."""
        c = read_report()
        assert "semanage port" in c and "http_port_t" in c, (
            "must reference semanage port -a -t http_port_t command"
        )

    def test_ausearch_avc(self):
        """Skill teaches 'ausearch -m AVC -ts recent' to find SELinux
        denials. Without skill, agents may describe generic audit log checks."""
        c = read_report()
        assert "ausearch" in c and "AVC" in c, (
            "must reference ausearch -m AVC for SELinux denial detection"
        )

    def test_firewall_permanent_flag(self):
        """Skill teaches using --permanent flag with firewall-cmd to
        persist firewall rules across reboots."""
        c = read_report()
        assert "--permanent" in c, (
            "must reference --permanent flag for persistent firewall rules"
        )

    def test_ssh_based_diagnosis(self):
        """Skill teaches SSH-based remote diagnosis workflow (not local
        MCP). Without skill, agents assume local execution."""
        c = read_report()
        assert "ssh" in c.lower() or "SSH" in c, (
            "must reference SSH-based remote diagnosis"
        )

    def test_systemctl_and_journalctl(self):
        """Skill teaches specific diagnostic sequence: systemctl status
        + journalctl for service debugging."""
        c = read_report()
        has_systemctl = "systemctl" in c
        has_journalctl = "journalctl" in c
        assert has_systemctl and has_journalctl, (
            "must reference both systemctl and journalctl for diagnosis"
        )
