"""Resolution advisor tests - documentation-backed recommendations, AAP specifics."""
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
        assert len(read_report()) > 400

class TestResolutionStructure:
    """Skill defines immediate, root cause, and preventive tiers."""
    def test_immediate_fix(self):
        c = read_report().lower()
        assert "immediate" in c or "now" in c or "urgent" in c or "quick" in c
    def test_root_cause_fix(self):
        c = read_report().lower()
        assert "root cause" in c or "prevent" in c or "permanent" in c
    def test_verification_steps(self):
        c = read_report().lower()
        assert "verif" in c or "confirm" in c or "test" in c

class TestAnsibleSpecifics:
    """Ansible-specific guidance for privilege escalation."""
    def test_privilege_escalation(self):
        c = read_report().lower()
        assert "privilege" in c or "escalation" in c or "become" in c or "sudo" in c
    def test_timeout_config(self):
        c = read_report().lower()
        assert "timeout" in c
    def test_ansible_config(self):
        c = read_report().lower()
        assert "ansible" in c

class TestDocumentation:
    """Must reference Red Hat documentation."""
    def test_red_hat_documentation(self):
        c = read_report().lower()
        assert "red hat" in c or "documentation" in c or "kb" in c or "knowledge base" in c

class TestReExecution:
    def test_re_execution_assessment(self):
        c = read_report().lower()
        assert "re-execut" in c or "relaunch" in c or "retry" in c or "safe" in c
