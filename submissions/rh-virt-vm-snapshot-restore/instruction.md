# VM Snapshot Restore Task

You are an OpenShift Virtualization administrator. Restore VM `production-db` from snapshot `production-db-backup-20240301` in namespace `prod-vms`.

## Scenario
The production database VM suffered data corruption after a failed migration. You need to restore it from the most recent good snapshot. This is a destructive operation — the current VM state will be replaced by the snapshot contents.

## Requirements
- Verify the snapshot is valid and ready to use for restore
- Determine if the VM needs to be stopped before restore can proceed
- Define the exact VirtualMachineRestore resource specification
- Describe how to monitor restore progress to completion

Write your restore plan in `/solution/report.md`.

Use MCP tools to examine the cluster. If reference documentation or skills are available in this environment, consult them before beginning work. Complete the entire analysis autonomously — do not stop for user confirmation.
