"""
Tests for rh-virt__vm-snapshot-list evaluation.

6 tests: 2 padding (both agents pass) + 4 skill-dependent.

Skill-dependent tests target knowledge ONLY available through the
SKILL.md workflow and its Common Issues section — NOT from general
KubeVirt knowledge or mock MCP data exploration.
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

    def test_mentions_production_db(self):
        c = read_report().lower()
        assert "production-db" in c or "production_db" in c, (
            "report must reference the target VM production-db"
        )


class TestSkillDependent:
    def test_label_selector_with_fallback(self):
        """SKILL Step 2 Note says: 'The label selector
        vm.kubevirt.io/name=<vm-name> may not always exist. If no results
        are returned, fall back to listing all snapshots and filtering by
        checking spec.source.name field.' Both strategies must be
        described as primary + fallback."""
        c = read_report().lower()
        has_label = "vm.kubevirt.io/name" in c
        has_fallback = any(t in c for t in [
            "spec.source.name", "spec.source",
            "fallback", "fall back",
            "filter by", "filtering by",
        ])
        assert has_label and has_fallback, (
            "must describe vm.kubevirt.io/name label selector as primary "
            "AND spec.source.name fallback strategy (SKILL Step 2 note)"
        )

    def test_events_list_for_diagnosis(self):
        """SKILL Issue 3 says: 'Check cluster events: Use events_list
        for snapshot-related errors.' This is a specific diagnostic tool
        call that the SKILL prescribes for failed snapshots. Control
        agents don't know to use events_list for this purpose."""
        c = read_report().lower()
        has_events = any(t in c for t in [
            "events_list", "events list",
            "cluster events", "event",
        ])
        has_failed = any(t in c for t in [
            "failed", "failure", "error",
        ])
        assert has_events and has_failed, (
            "must use events_list to diagnose failed snapshot "
            "(SKILL Issue 3 diagnostic step)"
        )

    def test_status_conditions_check(self):
        """SKILL Issue 3 says: 'Get snapshot details: Use resources_get
        to check status.conditions for error messages.' This is a
        specific field path that the SKILL prescribes for diagnosis."""
        c = read_report().lower()
        has_conditions = any(t in c for t in [
            "status.conditions", "conditions",
        ])
        has_diagnostic = any(t in c for t in [
            "resources_get", "diagnos", "investigat",
            "error message", "root cause",
        ])
        assert has_conditions and has_diagnostic, (
            "must check status.conditions on failed snapshot for error "
            "details (SKILL Issue 3 diagnostic step)"
        )

    def test_cross_namespace_discovery(self):
        """SKILL Issue 2 says: 'Check other namespaces: Use
        namespaces_list to see available namespaces.' The instruction
        asks about cross-namespace discovery. Control agents don't
        know to use namespaces_list for this purpose."""
        c = read_report().lower()
        has_ns = any(t in c for t in [
            "namespaces_list", "namespaces list",
            "other namespace", "cross-namespace",
            "multiple namespace",
        ])
        assert has_ns, (
            "must describe cross-namespace snapshot discovery using "
            "namespaces_list (SKILL Issue 2)"
        )
