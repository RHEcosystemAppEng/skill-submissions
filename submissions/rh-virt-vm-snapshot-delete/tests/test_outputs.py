"""
Tests for rh-virt__vm-snapshot-delete per-skill evaluation.

Dead-weight tests where both control and treatment pass 3/3 removed.
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


class TestSkillDependent:
    def test_spec_source_name(self):
        """Skill teaches reading spec.source.name to identify the source VM
        of a snapshot. Without skill, agents guess from the snapshot name."""
        c = read_report()
        assert "spec.source.name" in c, (
            "must reference spec.source.name to identify source VM"
        )

    def test_label_selector_for_siblings(self):
        """Skill teaches using vm.kubevirt.io/name labelSelector to find
        sibling snapshots, with fallback to spec.source.name filtering."""
        c = read_report()
        has_label = "vm.kubevirt.io/name" in c
        has_fallback = "spec.source.name" in c
        assert has_label or has_fallback, (
            "must use vm.kubevirt.io/name label or spec.source.name for sibling discovery"
        )

    def test_last_snapshot_warning(self):
        """Skill teaches counting sibling snapshots and warning when this
        is the ONLY snapshot for the VM - after deletion no recovery
        points exist. Without skill, agents delete without considering
        whether other snapshots remain."""
        c = read_report().lower()
        has_last = any(t in c for t in [
            "only snapshot", "last snapshot", "no snapshot",
            "no recovery", "sole snapshot",
        ])
        has_count = any(t in c for t in [
            "count snapshot", "snapshot count", "remaining snapshot",
            "other snapshot",
        ])
        assert has_last or has_count, (
            "must warn about last-snapshot-for-VM scenario"
        )

    def test_snapshot_count_before_delete(self):
        """Skill teaches counting remaining snapshots for the VM and
        presenting the count before deletion. Without skill, agents
        don't enumerate recovery points."""
        c = read_report().lower()
        has_number_near_snapshot = bool(re.search(
            r'\d+\s*(?:snapshot|recovery point|remaining)', c
        )) or bool(re.search(
            r'(?:snapshot|recovery point)s?\s*(?:remaining|left|found|exist|count)\s*[:\s]*\d+', c
        ))
        has_count_phrase = any(t in c for t in [
            "snapshot count", "number of snapshot",
            "remaining snapshot", "snapshots found",
        ])
        assert has_number_near_snapshot or has_count_phrase, (
            "must present snapshot count before deletion"
        )
