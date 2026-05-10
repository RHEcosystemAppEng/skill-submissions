# VM Snapshot Deletion Task

You are an OpenShift Virtualization administrator. Clean up old and failed snapshots in the cluster, and address a reported storage cleanup issue.

## Scenario
The team needs you to handle three snapshot cleanup tasks:

1. **Delete old backup**: Snapshot `vm-db-prod-01-backup-20260201` in namespace `virt-prod-dc2` is outdated and needs to be removed. Before deleting, verify it's safe: check for active VirtualMachineRestore resources referencing it, and count the remaining snapshots for the same VM. If this is the last snapshot, flag it clearly.

2. **Clean up failed snapshot**: Snapshot `vm-etl-prod-01-snap-failed` in namespace `virt-prod-dc1` is in a failed state. Assess whether it should be deleted or whether the underlying issue should be diagnosed first. Explain what diagnostic steps you would take.

3. **Storage cleanup failures**: The team has reported that previous snapshot deletions left behind orphaned storage — PVCs and DataVolumes were not freed after the snapshot was removed. Include a diagnostic and remediation plan for these storage cleanup failures, covering what causes them and the correct remediation sequence.

## Requirements
- For each snapshot: verify it exists, identify the source VM, list sibling snapshots
- Describe the safety confirmation protocol that SHOULD be followed before destructive operations (even though this task runs autonomously)
- Explain the exact MCP tool and parameters for deletion
- For orphaned storage: diagnose causes (finalizers, PV reclaim policy, CDI controller) and describe the correct deletion ordering
- Address what to do when MCP tools are insufficient for cleanup (e.g., force delete, finalizer removal)

Write your complete analysis and deletion plan in `/solution/report.md`.

**Important**: Before starting, check whether this environment provides reference documentation, skills, or other resources that can guide your approach. If tools, documentation, or structured workflows are available, use them to inform your analysis rather than working from general knowledge alone.

Use MCP tools to examine the cluster. Complete the entire analysis autonomously — do not stop for user confirmation.
