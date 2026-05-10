# VM Snapshot Creation Task

You are an OpenShift Virtualization administrator. A previous snapshot attempt for VM `vm-etl-prod-01` in namespace `virt-prod-dc1` failed. You need to diagnose WHY it failed and then plan a successful snapshot for VM `production-db` in namespace `prod-vms` before applying a critical patch.

## Scenario
A colleague attempted to snapshot `vm-etl-prod-01` but it failed with a timeout error. The failed snapshot object `vm-etl-prod-01-snap-failed` still exists in the cluster. You need to:
1. Investigate the failed snapshot and determine the root cause
2. Apply the lessons learned to plan a successful snapshot for `production-db`

The VM `production-db` is a database server that is currently running. You need to perform a comprehensive storage-level analysis to ensure all prerequisites are met before attempting the snapshot.

## Requirements
- Examine the failed snapshot `vm-etl-prod-01-snap-failed` and diagnose the storage-level root cause (not just the error message)
- Perform a complete storage prerequisite analysis for `production-db`: check the VM's volumeSnapshotStatuses, verify VolumeSnapshotClass matches the CSI driver, and confirm CSI snapshot capabilities
- Determine the snapshot consistency level you will achieve for `production-db` and explain your reasoning based on guest agent status
- Identify any conditions that would block snapshot creation (hot-plugged volumes, storage incompatibilities)
- Define the exact VirtualMachineSnapshot CR YAML specification including the correct apiVersion and source fields
- Explain which MCP tool is used to create the snapshot and why

Write your complete analysis and snapshot plan in `/solution/report.md`.

**Important**: Before starting, check whether this environment provides reference documentation, skills, or other resources that can guide your approach. If tools, documentation, or structured workflows are available, use them to inform your analysis rather than working from general knowledge alone.

Use MCP tools to examine the cluster. Complete the entire analysis autonomously — do not stop for user confirmation.
