"""
Tests for rh-basic__red-hat-product-lifecycle evaluation.
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

    def test_mentions_lifecycle(self):
        c = read_report().lower()
        assert any(t in c for t in ["lifecycle", "life cycle", "support", "eol"]), (
            "report should mention product lifecycle"
        )

    def test_report_has_structure(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"


class TestSkillDependent:
    def test_backporting_model(self):
        """SKILL versioning section: Red Hat backports security fixes into
        shipped versions rather than rebasing to upstream. Without skill,
        agents say 'upgrade to latest OpenSSL'."""
        c = read_report().lower()
        assert "backport" in c, (
            "should explain Red Hat's backporting model"
        )

    def test_package_version_format(self):
        """SKILL versioning section: format is name-version-release.elX.
        The release counter increments for each backported fix.
        Without skill, agents don't parse the format."""
        c = read_report().lower()
        assert any(t in c for t in [
            "name-version-release", "version-release",
            ".el8", ".el9", "release counter",
            "1.1.1k", "7.el8",
        ]), "should explain RHEL package version format (name-version-release.elX)"

    def test_ocp_18_month_lifecycle(self):
        """SKILL OCP lifecycle: 18-month lifecycle per minor version.
        Without skill, agents give vague 'check Red Hat docs' answers."""
        c = read_report().lower()
        assert "18" in c and "month" in c, (
            "should state OCP 4.x has 18-month lifecycle per minor version"
        )

    def test_eus_mention(self):
        """SKILL lifecycle phases: EUS = 24-month minor release freeze for
        even minors. Without skill, agents don't mention EUS availability."""
        c = read_report().lower()
        assert "eus" in c, (
            "should mention EUS (Extended Update Support) availability"
        )

    def test_rhel_support_phases(self):
        """SKILL lifecycle phases: Full Support (~yr 1-5) and Maintenance
        Support (~yr 5-10) with different update scopes."""
        c = read_report().lower()
        has_full = "full support" in c
        has_maint = "maintenance" in c and "support" in c
        assert has_full and has_maint, (
            "should distinguish Full Support and Maintenance Support phases"
        )

    def test_abi_stability(self):
        """SKILL versioning section: RHEL guarantees ABI compatibility within
        a major version. Without skill, agents don't mention this guarantee."""
        c = read_report().lower()
        assert any(t in c for t in [
            "abi", "compatibility", "binary compatibility",
        ]), "should mention RHEL ABI/API stability guarantee within major version"
