# VM Snapshot Listing Task

You are an OpenShift Virtualization administrator. Produce a complete inventory of all snapshots for VM `production-db` in namespace `prod-vms`.

## Scenario
The team needs to understand all available recovery points for the production database VM. Some snapshots may have been created automatically, others manually. You need to list them with status, readiness, and identify any that are failed or not usable for restore.

## Requirements
- List all snapshots associated with the VM
- For each snapshot report: name, creation time, status phase, and whether it is ready to use
- Identify failed or incomplete snapshots and suggest troubleshooting
- Explain your discovery method for finding associated snapshots

Write the snapshot inventory in `/solution/report.md`.

Use MCP tools to query snapshot data. If reference documentation or skills are available in this environment, consult them before beginning work. Complete the entire analysis autonomously — do not stop for user confirmation.
