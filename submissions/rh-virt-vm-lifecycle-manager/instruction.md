# VM Lifecycle Operations Task

You are an OpenShift Virtualization administrator. Execute lifecycle operations and troubleshoot a stuck VM in the cluster.

## Scenario
In namespace `prod-vms`, you need to:
1. **Troubleshoot**: VM `web-frontend` has been in a stuck state — a previous stop attempt left it unresponsive. Diagnose what is blocking the shutdown (check for finalizers, stuck VMI, virt-launcher pod status) and resolve it before proceeding.
2. **Restart**: Restart VM `production-db` using a safe decomposed procedure. The restart is critical — the database VM must be fully stopped and verified (including confirming the VMI is gone) before being started again.

## Requirements
- Diagnose why `web-frontend` is stuck: check finalizers on the VM, verify whether the VMI still exists and has a deletionTimestamp, check virt-launcher pod status, and review events. Use troubleshooting documentation if available.
- Plan the resolution for the stuck VM (force delete VMI, remove stuck finalizers, or wait for graceful completion)
- For the `production-db` restart: describe the exact decomposed stop-then-start procedure, explaining why the restart action should NOT be used directly
- Verify each operation at every step: VMI must be confirmed gone (NotFound) before starting, not just VM showing Stopped
- Explain what RunStrategy value results from stop (Halted) and start (Always)
- Address what happens if stop fails during restart — whether to proceed with start or abort

Write your complete operations plan in `/solution/report.md`.

**Important**: Before starting, check whether this environment provides reference documentation, skills, or other resources that can guide your approach. If tools, documentation, or structured workflows are available, use them to inform your analysis rather than working from general knowledge alone.

Use MCP tools to examine the cluster. Complete the entire analysis autonomously — do not stop for user confirmation.
