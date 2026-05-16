"""
Tests for rh-developer-rhel-deploy per-skill evaluation.

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
    def test_rootless_vs_rootful_strategy(self):
        """Skill teaches the dual strategy fork: Container (Podman+systemd)
        vs Native (dnf+systemd), with rootless vs rootful decision.
        Without skill, agents only describe rootful deployment."""
        c = read_report().lower()
        assert "rootless" in c, (
            "must address rootless deployment option"
        )

    def test_rootless_systemd_path(self):
        """Skill teaches rootless systemd service location
        ~/.config/systemd/user/ for user-level units. Without skill,
        agents only know /etc/systemd/system/ for rootful."""
        c = read_report()
        assert ".config/systemd/user" in c, (
            "must reference rootless systemd path (~/.config/systemd/user/)"
        )

    def test_enable_linger(self):
        """Skill teaches loginctl enable-linger as required for rootless
        user services to survive logout. Without skill, agents miss
        this critical requirement."""
        c = read_report().lower()
        assert "enable-linger" in c or "loginctl" in c, (
            "must mention loginctl enable-linger for rootless services"
        )

    def test_mock_host_profile(self):
        """Skill-equipped agents discover the host profile via MCP:
        RHEL 9.3, Podman 4.9.4. Without skill, agents write generic
        plans without host-specific context."""
        c = read_report()
        assert "9.3" in c or "4.9.4" in c, (
            "must reference host profile from MCP "
            "(RHEL 9.3, Podman 4.9.4)"
        )

    def test_selinux_volume_labels(self):
        """Skill teaches SELinux volume labels :z (shared) and :Z
        (private) for container mounts. Without skill, agents skip
        SELinux mount context entirely."""
        c = read_report()
        assert ":z" in c or ":Z" in c, (
            "must specify SELinux volume labels (:z shared, :Z private)"
        )

    def test_systemd_hardening_directives(self):
        """Skill teaches specific systemd hardening directives:
        NoNewPrivileges, ProtectSystem, ReadWritePaths. Without skill,
        agents create basic unit files without security hardening."""
        c = read_report()
        directives = [
            "NoNewPrivileges", "ProtectSystem", "ReadWritePaths",
            "PrivateTmp", "ProtectHome",
        ]
        found = sum(1 for d in directives if d in c)
        assert found >= 2, (
            "must include at least 2 systemd hardening directives "
            "(NoNewPrivileges, ProtectSystem, ReadWritePaths, etc.)"
        )
