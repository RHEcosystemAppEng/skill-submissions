# VM Lifecycle Operations Task

You are an OpenShift Virtualization administrator. Execute lifecycle operations for VMs in the cluster.

## Scenario
In namespace `prod-vms`, you need to stop the VM `web-frontend` and restart the VM `production-db`. The restart is critical — the database VM must be fully stopped and verified before being started again to avoid data corruption from resourceVersion conflicts.

## Requirements
- Plan the exact procedure for each operation
- Describe how to verify each operation completed successfully
- Explain what RunStrategy value results from each operation
- Address error handling if an operation fails or the VM is already in the target state

Write your complete operations plan in `/solution/report.md`.

Use MCP tools to examine the cluster. If reference documentation or skills are available in this environment, consult them before beginning work. Complete the entire analysis autonomously — do not stop for user confirmation.
