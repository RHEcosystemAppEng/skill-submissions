"""
Tests for rh-basic red-hat-product-lifecycle skill evaluation.
Tests check for SKILL-specific Red Hat lifecycle and versioning knowledge.
"""
import os
import re
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

    def test_report_has_content(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"

    def test_mentions_rhel(self):
        content = read_report().upper()
        assert "RHEL" in content, "report should mention RHEL"


class TestSkillDependent:
    def test_rhel_10_year_lifecycle(self):
        """SKILL: RHEL 8/9/10 has 10-year lifecycle.
        Full Support (~yr 1-5), Maintenance Support (~yr 5-10), Extended Life."""
        c = read_report().lower()
        has_phases = sum(1 for p in [
            "full support", "maintenance support", "extended life",
        ] if p in c)
        assert has_phases >= 2, (
            f"must describe RHEL lifecycle phases "
            f"(Full Support/Maintenance Support/Extended Life); found {has_phases}/3"
        )

    def test_rhel_86_lifecycle_assessment(self):
        """Task requires: RHEL 8.6 lifecycle status with concrete dates."""
        c = read_report().lower()
        assert "8.6" in c, "must address RHEL 8.6 specifically"
        has_date = bool(re.search(r"\d{4}", c))
        assert has_date, "must include concrete dates for RHEL 8.6"

    def test_ocp_414_lifecycle(self):
        """Task requires: OpenShift 4.14 lifecycle status and EUS availability."""
        c = read_report().lower()
        assert "4.14" in c, "must address OpenShift 4.14 specifically"

    def test_ocp_18_month_lifecycle(self):
        """SKILL: OCP 4.x has 18-month lifecycle per minor.
        Full Support 6 months, then Maintenance Support."""
        c = read_report().lower()
        has_ocp = any(t in c for t in [
            "18 month", "18-month", "eighteen month",
            "6 month", "6-month",
        ])
        assert has_ocp, (
            "must describe OCP minor version lifecycle duration "
            "(SKILL: 18-month lifecycle, 6-month full support)"
        )

    def test_eus_knowledge(self):
        """SKILL: EUS for even OCP minors (4.12, 4.14, 4.16).
        24-month minor release freeze for RHEL."""
        c = read_report().lower()
        has_eus = any(t in c for t in [
            "eus", "extended update support", "extended update",
        ])
        assert has_eus, (
            "must discuss EUS (Extended Update Support) for OCP 4.14 "
            "(SKILL: EUS for even minors)"
        )

    def test_backporting_model(self):
        """SKILL: Red Hat backports security fixes into shipped version.
        Version numbers look 'old' but carry all critical CVE fixes.
        This is the KEY differentiator for the openssl question."""
        c = read_report().lower()
        has_backport = any(t in c for t in [
            "backport", "back-port", "backported",
        ])
        assert has_backport, (
            "must explain Red Hat's backporting model "
            "(SKILL: fixes backported into shipped version, not rebased)"
        )

    def test_package_version_format(self):
        """SKILL: name-version-release.elX format.
        openssl-1.1.1k-7.el8 -> version=1.1.1k, release=7, elX=el8."""
        c = read_report().lower()
        has_format = any(t in c for t in [
            "1.1.1k", "openssl", "-7.el8", ".el8",
            "name-version-release", "release counter",
        ])
        assert has_format, (
            "must explain the package version format (name-version-release.elX) "
            "for the openssl question"
        )

    def test_openssl_not_outdated_explanation(self):
        """Task: explain why openssl-1.1.1k-7.el8 flagged as 'outdated' is still secure.
        SKILL: never use upstream version as measure of patch currency."""
        c = read_report().lower()
        has_explanation = any(t in c for t in [
            "not outdated", "still.*patch", "still.*secur",
            "fully patched", "security fixes",
            "upstream version", "not.*measure",
            "scanner", "false positive",
        ])
        assert has_explanation, (
            "must explain why the 'outdated' openssl is actually still patched "
            "(SKILL: backporting model)"
        )

    def test_concrete_dates_not_relative(self):
        """SKILL: state dates concretely ('ends May 31, 2025'), never relatively."""
        c = read_report()
        has_concrete = bool(re.search(
            r"(20\d{2}[-/]\d{2}|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+20\d{2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+20\d{2}|\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+20\d{2})",
            c
        ))
        assert has_concrete, (
            "must use concrete dates (SKILL: never use relative dates)"
        )

    def test_actionable_recommendation(self):
        """SKILL: each phase has specific action recommendation."""
        c = read_report().lower()
        has_action = any(t in c for t in [
            "upgrade", "migration", "plan", "recommend",
            "action", "apply updates", "security patches only",
        ])
        assert has_action, (
            "must include actionable recommendations per lifecycle phase"
        )
