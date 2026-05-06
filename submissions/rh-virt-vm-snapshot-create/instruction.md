# VM Snapshot Creation Task

You are an OpenShift Virtualization administrator. Create a snapshot of a running VM `production-db` in namespace `prod-vms` before applying a critical patch.

## Scenario
The VM `production-db` is a database server that is currently running. It may or may not have the QEMU guest agent installed. It has multiple disks including some that may have been hot-plugged. You need to plan and execute a snapshot while understanding exactly what consistency level you will achieve and what blockers might prevent the snapshot.

## Requirements
- Check all prerequisites that must exist before a snapshot can be created
- Determine the snapshot consistency level you will achieve for this specific VM and explain your reasoning
- Identify any conditions that would block snapshot creation entirely
- Define the snapshot CR specification
- Describe how to monitor snapshot progress and interpret the results

Write your complete snapshot plan in `/solution/report.md`.

Use MCP tools to examine the cluster. If reference documentation or skills are available in this environment, consult them before beginning work. Complete the entire analysis autonomously — do not stop for user confirmation.
