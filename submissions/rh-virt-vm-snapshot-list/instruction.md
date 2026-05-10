# VM Snapshot Listing and Diagnosis Task

You are an OpenShift Virtualization administrator. Produce a complete snapshot inventory for VM `production-db` in namespace `prod-vms`, with root cause analysis for any failed snapshots.

## Scenario
The team needs a full picture of all recovery points for the production database VM. One of the snapshots is known to have failed, and the team needs to understand WHY — not just see the error message.

Additionally, there is concern that snapshots for this VM might exist in other namespaces due to a previous migration. You need to describe your discovery strategy and verify.

## Requirements
1. **Inventory**: List ALL snapshots for `production-db` in `prod-vms`, reporting for each: name, creation time, status phase, readyToUse, and consistency indications
2. **Discovery strategy**: Describe how you find snapshots associated with a VM. Explain your primary method and what fallback you would use if the primary returns no results (e.g., label selector vs iterating all snapshots and checking spec.source.name)
3. **Failed snapshot root cause**: For any failed snapshot, go beyond the error message. Use events (events_list) and check snapshot status.conditions to diagnose the underlying cause. Reference storage prerequisites (VolumeSnapshotClass, CSI driver) if relevant
4. **Cross-namespace check**: Describe how you would verify whether snapshots exist in other namespaces for the same VM, using namespaces_list to enumerate candidate namespaces
5. **Recommendations**: For failed snapshots, recommend whether to delete and retry or fix the underlying issue first

Write the snapshot inventory and analysis in `/solution/report.md`.

**Important**: Before starting, check whether this environment provides reference documentation, skills, or other resources that can guide your approach. If tools, documentation, or structured workflows are available, use them to inform your analysis rather than working from general knowledge alone.

Use MCP tools to query snapshot data. Complete the entire analysis autonomously — do not stop for user confirmation.
