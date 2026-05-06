# VM Snapshot Deletion Task

You are an OpenShift Virtualization administrator. A snapshot named `production-db-backup-20240215` for VM `production-db` in namespace `prod-vms` needs to be cleaned up.

## Scenario
The snapshot is old and consuming storage. Before deleting, you must verify it is safe to remove — no active restores should depend on it, and the team should be warned if it is the only remaining recovery point.

## Requirements
- Verify the snapshot exists and identify its source VM
- Check for any active VirtualMachineRestore resources that reference this snapshot
- List sibling snapshots to determine if this is the last recovery point
- Plan the deletion with appropriate safety checks

Write your deletion plan in `/solution/report.md`.

Use MCP tools to examine the cluster. If reference documentation or skills are available in this environment, consult them before beginning work. Complete the entire analysis autonomously — do not stop for user confirmation.
