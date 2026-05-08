"""
Tests for rh-virt__vm-snapshot-list per-skill evaluation.

Exact-field tests: require API field paths and GVKs that only SKILL.md teaches.
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

    def test_mentions_snapshot(self):
        content = read_report().lower()
        assert "snapshot" in content

    def test_report_has_structure(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"


class TestSkillDependent:
    def test_snapshot_gvk(self):
        """Skill teaches snapshot.kubevirt.io/v1beta1 as the apiVersion
        for VirtualMachineSnapshot listing."""
        c = read_report()
        assert "snapshot.kubevirt.io/v1beta1" in c, (
            "must reference snapshot.kubevirt.io/v1beta1 GVK"
        )

    def test_ready_to_use_field(self):
        """Skill teaches status.readyToUse as the field that indicates
        whether a snapshot can be used for restore. Without skill,
        agents only check status.phase."""
        c = read_report()
        assert "readyToUse" in c, (
            "must reference status.readyToUse field"
        )

    def test_label_selector_with_fallback(self):
        """Skill teaches using vm.kubevirt.io/name labelSelector first,
        then falling back to filtering by spec.source.name if labels
        are missing. Without skill, agents use only one method."""
        c = read_report()
        has_label = "vm.kubevirt.io/name" in c
        has_source = "spec.source.name" in c
        assert has_label or has_source, (
            "must use vm.kubevirt.io/name label or spec.source.name for discovery"
        )

    def test_status_phase_values(self):
        """Skill teaches exact status.phase values: InProgress, Succeeded,
        Failed. Without skill, agents use generic status descriptions."""
        c = read_report()
        for phase in ["InProgress", "Succeeded", "Failed"]:
            assert phase in c, (
                f"must reference exact phase value: {phase}"
            )

    def test_ready_to_use_false_troubleshooting(self):
        """Skill teaches that readyToUse == false is the trigger for
        troubleshooting. Generic 'conditions' appears everywhere."""
        c = read_report()
        has_ready_false = (
            "readyToUse" in c
            and ("false" in c.lower() or "not ready" in c.lower())
        )
        assert has_ready_false, (
            "must reference readyToUse == false as troubleshooting trigger"
        )

    def test_creation_timestamp_age(self):
        """Skill teaches calculating and displaying Age from
        metadata.creationTimestamp. Without skill, agents show raw
        timestamps or omit age entirely."""
        c = read_report().lower()
        has_age = "age" in c
        has_timestamp = "creationtimestamp" in c
        assert has_age or has_timestamp, (
            "must display age calculated from metadata.creationTimestamp"
        )

    def test_table_display_format(self):
        """Skill teaches a specific table format with columns: Snapshot
        Name, VM Name, Status, Created, Age, ReadyToUse. Without skill,
        agents present data as unstructured text."""
        c = read_report()
        pipe_count = c.count("|")
        assert pipe_count >= 6, (
            "must present snapshots in a structured table format"
        )

    def test_resources_list_tool(self):
        """Skill teaches using resources_list MCP tool with the snapshot
        GVK. Without skill, agents use kubectl or generic API calls."""
        c = read_report()
        assert "resources_list" in c, (
            "must use resources_list MCP tool for snapshot discovery"
        )
