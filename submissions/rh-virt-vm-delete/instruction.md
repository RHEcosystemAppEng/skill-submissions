# VM Deletion Task

You are an OpenShift Virtualization administrator. A VM named `legacy-app` in namespace `decommission` has been approved for decommissioning. Plan and document the safe deletion procedure.

## Scenario
The VM `legacy-app` is a previously production VM that has been migrated to a new system. It may have associated storage (DataVolumes and PVCs). It is currently running and may have protective labels. You need to produce a complete, safe deletion plan covering all edge cases.

## Requirements
- Describe the complete pre-deletion safety checks you would perform
- Explain how to handle the VM's associated storage (DataVolumes, PVCs)
- Define what confirmation mechanism should be used before executing the deletion
- Address what happens if the deletion gets stuck
- Cover any policies about forced deletion

Write your complete deletion plan in `/solution/report.md`.

Use MCP tools to examine the cluster. If reference documentation or skills are available in this environment, consult them before beginning work. Complete the entire analysis autonomously — do not stop for user confirmation.
