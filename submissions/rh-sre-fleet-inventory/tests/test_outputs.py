"""
Tests for rh-sre__fleet-inventory per-skill evaluation.

Skill-specific knowledge tested:
- Stale = <7 days check-in (stale boolean field, last_seen)
- Per-system CVE status strings: Vulnerable, Patched, Not Affected
- System UUID tracking for remediation follow-up
- get_host_details for fleet vs get_cve_systems for CVE queries
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

    def test_mentions_topic(self):
        content = read_report().lower()
        assert any(t in content for t in ["system", "host", "fleet", "inventory"]), (
            "report should mention key topic"
        )

    def test_report_has_structure(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"


class TestSkillDependent:
    def test_stale_7_day_heuristic(self):
        """Skill: Stale systems are those that haven't checked in within 7
        days (stale boolean field, last_seen timestamp). Without skill,
        agents use arbitrary thresholds or skip staleness checks."""
        c = read_report().lower()
        has_stale = any(t in c for t in [
            "stale", "last_seen", "last seen",
            "last check-in", "last checkin",
        ])
        has_threshold = any(t in c for t in [
            "7 day", "7 days", "seven day", "week",
        ])
        assert has_stale and has_threshold, (
            "should flag stale systems using <7 day check-in heuristic "
            "(skill: stale boolean field, 7-day threshold)"
        )

    def test_per_system_vulnerability_status(self):
        """Skill: Per-system CVE status uses specific strings: Vulnerable,
        Patched, Not Affected. Without skill, agents use generic terms."""
        c = read_report().lower()
        status_strings = sum(1 for t in [
            "vulnerable", "patched", "not affected",
        ] if t in c)
        assert status_strings >= 2, (
            "should use specific per-system vulnerability status strings: "
            "Vulnerable, Patched, Not Affected (skill: get_cve_systems response)"
        )

    def test_system_uuid_tracking(self):
        """Skill: Track system UUIDs (not just hostnames) to enable
        programmatic remediation API calls. Without skill, agents
        only list display names."""
        c = read_report().lower()
        has_uuid = any(t in c for t in [
            "system_id", "system id", "uuid", "system_uuid",
            "identifier",
        ])
        has_followup = any(t in c for t in [
            "remediat", "follow-up", "follow up", "action",
            "track", "subsequent",
        ])
        assert has_uuid and has_followup, (
            "should track system UUIDs for remediation follow-up "
            "(skill: system_id for API calls)"
        )

    def test_rhel_version_distribution(self):
        """Skill: Report RHEL version distribution across fleet."""
        c = read_report().lower()
        assert any(t in c for t in [
            "rhel 7", "rhel 8", "rhel 9",
            "rhel7", "rhel8", "rhel9",
            "el7", "el8", "el9",
            "version distribution", "rhel version",
        ]), (
            "should report RHEL version distribution across the fleet"
        )

    def test_unsupported_rhel_flagged(self):
        """Skill: Flag systems running unsupported/EOL RHEL versions as
        compliance risks."""
        c = read_report().lower()
        assert any(t in c for t in [
            "unsupported", "end of life", "eol", "end-of-life",
            "deprecated", "out of support",
        ]), (
            "should flag unsupported RHEL versions as compliance risk"
        )

    def test_next_steps_offered(self):
        """Skill: Offer transition to remediation workflow for vulnerable
        systems."""
        c = read_report().lower()
        assert any(t in c for t in [
            "next step", "remediate", "playbook",
            "remediation", "action item",
        ]), (
            "should offer next steps for remediation of vulnerable systems"
        )
