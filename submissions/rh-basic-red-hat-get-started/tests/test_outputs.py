"""Red Hat Get Started (skills installer) tests."""
import os, pytest

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
        assert len(read_report()) > 300

class TestSkillsList:
    """The 5 specific skills are defined in the SKILL.md."""
    def test_cve_explainer(self):
        assert "red-hat-cve-explainer" in read_report().lower() or "cve explainer" in read_report().lower()
    def test_diagnostics(self):
        assert "red-hat-diagnostics" in read_report().lower() or "diagnostics" in read_report().lower()
    def test_product_lifecycle(self):
        assert "red-hat-product-lifecycle" in read_report().lower() or "product lifecycle" in read_report().lower()
    def test_security_mcp_setup(self):
        assert "red-hat-security-mcp-setup" in read_report().lower() or "security mcp" in read_report().lower()
    def test_support_severity(self):
        assert "red-hat-support-severity" in read_report().lower() or "support severity" in read_report().lower()

class TestSkillsRepo:
    """Must reference the specific SKILLS_REPO URL."""
    def test_skills_repo_url(self):
        c = read_report()
        assert "agentic-collections" in c or "RHEcosystemAppEng" in c

class TestInstallerWorkflow:
    """Installer-specific behaviors: post-install summary and self-destruct."""
    def test_post_install_summary(self):
        c = read_report().lower()
        assert "install" in c and ("summary" in c or "available" in c or "command" in c)
    def test_failure_handling(self):
        c = read_report().lower()
        assert "fail" in c or "error" in c or "manual" in c
    def test_self_destruct(self):
        c = read_report().lower()
        assert "self" in c or "remov" in c or "delet" in c
