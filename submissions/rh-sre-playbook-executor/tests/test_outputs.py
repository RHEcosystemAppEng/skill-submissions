"""
Tests for rh-sre__playbook-executor per-skill evaluation.

Skill-specific knowledge tested:
- AAP has NO launch-time playbook override; Git sync is mandatory
- Dry-run uses job_type "check" (not a separate tool)
- Partial failure retry targets only failed hosts
- Template playbook path mismatch requires Git Flow before launch
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

    def test_mentions_topic(self):
        content = read_report().lower()
        assert any(t in content for t in ["playbook", "execut", "job"]), (
            "report should mention key topic"
        )

    def test_report_has_structure(self):
        content = read_report()
        assert len(content) > 200, "report should have substantial content"


class TestSkillDependent:
    def test_no_launch_override(self):
        """Skill: AAP has NO launch-time playbook override. You cannot specify
        a different playbook at launch time. The job runs whatever playbook
        the synced SCM project contains. Without skill, agents assume they
        can pass a playbook path at launch."""
        c = read_report().lower()
        has_no_override = any(t in c for t in [
            "no override", "cannot override", "no way to override",
            "can't override", "not possible to override",
            "no launch-time", "cannot specify",
            "cannot change the playbook at launch",
        ])
        has_sync_required = any(t in c for t in [
            "sync", "git", "commit", "push",
            "scm", "repository", "must be in the repo",
        ])
        assert has_no_override or has_sync_required, (
            "should state that AAP cannot override playbook at launch; "
            "Git sync is required (skill: 'there is no override at launch')"
        )

    def test_git_flow_before_launch(self):
        """Skill: Git commit/push/sync is BLOCKING before ANY launch (dry-run
        or production). The template points to cve-remediation.yml but we have
        remediation-CVE-2026-1234.yml — path mismatch = mandatory Git Flow.
        Without skill, agents launch immediately."""
        c = read_report().lower()
        has_git = any(t in c for t in ["git", "commit", "push"])
        has_before = any(t in c for t in [
            "before launch", "before execution", "before running",
            "before dry", "before any", "must first", "prerequisite",
            "blocking", "mandatory",
        ])
        assert has_git and has_before, (
            "should require Git commit/push BEFORE any launch "
            "(skill: Git Flow is BLOCKING before Phase 3)"
        )

    def test_path_mismatch_identified(self):
        """Skill: When template points to different playbook (cve-remediation.yml
        vs remediation-CVE-2026-1234.yml), this is a path mismatch requiring
        Git Flow. Without skill, agents ignore the mismatch."""
        c = read_report().lower()
        has_mismatch = any(t in c for t in [
            "different playbook", "path mismatch", "path differs",
            "different path", "points to", "cve-remediation",
            "not the same", "wrong playbook",
        ])
        has_resolution = any(t in c for t in [
            "update", "replace", "write", "git", "sync", "commit",
        ])
        assert has_mismatch and has_resolution, (
            "should identify playbook path mismatch and explain resolution"
        )

    def test_dry_run_job_type_check(self):
        """Skill: Dry-run uses job_type 'check' (Ansible check mode), not a
        separate API or tool. Without skill, agents may invent a separate
        dry-run endpoint."""
        c = read_report().lower()
        assert any(t in c for t in [
            "check mode", "check_mode", "job_type", "job type",
            '"check"', "'check'",
        ]), (
            "should specify dry-run via job_type 'check' / Ansible check mode "
            "(skill: same launch tool, different job_type)"
        )

    def test_relaunch_failed_hosts_only(self):
        """Skill: On partial failure, relaunch targets ONLY failed hosts
        (hosts: 'failed'), not all hosts. Without skill, agents re-run
        the entire job."""
        c = read_report().lower()
        has_relaunch = any(t in c for t in ["relaunch", "re-launch", "retry"])
        has_failed_only = any(t in c for t in [
            "failed hosts", "only failed", "hosts that failed",
            'hosts: "failed"', "hosts: 'failed'", "failed only",
        ])
        assert has_relaunch and has_failed_only, (
            "should relaunch targeting only failed hosts, not all "
            "(skill: jobs_relaunch_retrieve with hosts: 'failed')"
        )

    def test_no_direct_ansible_execution(self):
        """Skill: Execution goes through AAP job templates, never by running
        ansible-playbook directly. Without skill, agents may suggest running
        ansible-playbook on the CLI."""
        c = read_report().lower()
        uses_aap = any(t in c for t in [
            "job template", "aap", "automation platform",
            "launch", "job_templates",
        ])
        assert uses_aap, (
            "should execute through AAP job templates, not ansible-playbook CLI"
        )
