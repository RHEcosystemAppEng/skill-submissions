"""
Tests for rh-basic__red-hat-diagnostics evaluation.
Baseline tests: any competent agent should pass.
Skill-dependent tests: require knowledge from SKILL.md.
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

    def test_mentions_diagnostics(self):
        c = read_report().lower()
        assert any(t in c for t in ["diagnostic", "sos", "must-gather", "support"]), (
            "report should mention diagnostic data collection"
        )

    def test_report_has_structure(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"


class TestSkillDependent:
    def test_sos_report_with_plugins(self):
        """SKILL RHEL section: 'sos report' with '--only-plugins' for specific
        subsystems. Without skill, agents just say 'run sos report'."""
        c = read_report().lower()
        has_sos = "sos report" in c
        has_plugins = "--only-plugins" in c or "only-plugins" in c
        assert has_sos and has_plugins, (
            "should include 'sos report --only-plugins' for targeted RHEL diagnostics"
        )

    def test_oc_adm_must_gather(self):
        """SKILL OCP section: 'oc adm must-gather' for OpenShift.
        Without skill, agents might suggest 'oc logs' or 'oc describe'."""
        c = read_report().lower()
        assert "oc adm must-gather" in c, (
            "should include 'oc adm must-gather' for OpenShift diagnostics"
        )

    def test_aap_26_ocp_must_gather_image(self):
        """SKILL AAP section: AAP 2.6 OCP-based uses specific image
        'aap-must-gather-rhel9'. This is version-specific -- AAP 2.5 uses
        'aap-must-gather-rhel8'. Without skill, agents don't know this image."""
        c = read_report().lower()
        assert "aap-must-gather-rhel9" in c, (
            "should use AAP 2.6 specific must-gather image (aap-must-gather-rhel9)"
        )

    def test_data_sensitivity_warning(self):
        """SKILL sharing section: warns about sensitive data in archives
        before sharing. Without skill, agents skip this warning."""
        c = read_report().lower()
        assert any(t in c for t in [
            "sensitive", "redact", "review",
            "secrets", "credentials",
        ]) and any(t in c for t in [
            "archive", "report", "diagnostic", "data",
        ]), "should warn about sensitive data in diagnostic archives"

    def test_upload_instructions(self):
        """SKILL sharing section: attach at access.redhat.com/support or
        use ftp://dropbox.redhat.com for large files."""
        c = read_report().lower()
        assert any(t in c for t in [
            "access.redhat.com", "dropbox.redhat.com",
            "customer portal", "support case",
        ]), "should include upload instructions for Red Hat Support"

    def test_aap_ns_gather_command(self):
        """SKILL AAP OCP section: uses '-- /usr/bin/ns-gather <namespace>' flag.
        Without skill, agents use generic must-gather without ns-gather."""
        c = read_report().lower()
        assert "ns-gather" in c, (
            "should use ns-gather command for AAP OCP operator diagnostics"
        )
