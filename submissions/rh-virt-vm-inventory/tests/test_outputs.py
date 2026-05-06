"""
Tests for rh-virt__vm-inventory per-skill evaluation.

Exact-field tests: require API field paths that only SKILL.md teaches.
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

    def test_has_structured_data(self):
        content = read_report()
        has_table = "|" in content and content.count("|") >= 4
        has_list = content.count("- ") >= 5
        assert has_table or has_list, "report should present inventory in structured format"

    def test_mentions_namespace(self):
        content = read_report().lower()
        assert "namespace" in content


class TestSkillDependent:
    def test_storage_capacity_field_path(self):
        """Skill teaches summing storage from
        status.volumeStatus[].persistentVolumeClaimInfo.capacity.storage
        on VMI, excluding container disks and cloud-init.
        Without skill, agents don't know this nested path."""
        c = read_report()
        has_volume_status = "volumeStatus" in c or "persistentVolumeClaimInfo" in c
        assert has_volume_status, (
            "must reference volumeStatus or persistentVolumeClaimInfo for storage"
        )

    def test_guest_os_info_field(self):
        """Skill teaches reading guest OS from status.guestOSInfo.prettyName
        (or .name + version) on VMI. Without skill, agents guess OS from
        the image name."""
        c = read_report()
        assert "guestOSInfo" in c, (
            "must reference guestOSInfo field for OS detection"
        )

    def test_agent_connected_condition(self):
        """Skill teaches checking AgentConnected condition from VMI
        status.conditions. Without skill, agents skip guest agent health."""
        c = read_report()
        assert "AgentConnected" in c, (
            "must reference AgentConnected condition from VMI"
        )

    def test_vmi_for_runtime_data(self):
        """Skill teaches querying VirtualMachineInstance (separate from VM)
        for live runtime data: nodeName, IP, guestOS, conditions.
        Without skill, agents query only VirtualMachine objects."""
        c = read_report()
        assert "VirtualMachineInstance" in c or "VMI" in c, (
            "must distinguish VirtualMachineInstance for runtime data"
        )

    def test_interfaces_ip_field(self):
        """Skill teaches reading IP from status.interfaces[0].ipAddress
        on VMI. Without skill, agents use generic network lookup."""
        c = read_report()
        has_interfaces = "status.interfaces" in c or "interfaces[" in c
        has_ip = "ipAddress" in c
        assert has_interfaces or has_ip, (
            "must reference status.interfaces[].ipAddress for VM IP"
        )
