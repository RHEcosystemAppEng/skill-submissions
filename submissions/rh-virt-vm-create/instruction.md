# VM Creation Task

You are an OpenShift Virtualization administrator. The development team needs a new RHEL 9 VM for testing.

## Scenario
Provision a VM named `test-vm` in namespace `vm-testing` with 2 CPUs, 4Gi memory, and a 30Gi root disk. The cluster may have scheduling constraints, missing operators, or storage limitations that could prevent successful provisioning. You need to diagnose readiness and produce a complete provisioning plan with troubleshooting guidance.

## Requirements
- Assess cluster readiness for VM provisioning
- Define the complete VM resource specification
- Identify the correct storage class and explain your selection
- Describe how to verify the VM reached a healthy state after creation
- Document troubleshooting steps for common provisioning failures

Write your complete provisioning plan in `/solution/report.md`.

**Important**: Before starting, check whether this environment provides reference documentation, skills, or other resources that can guide your approach. If tools, documentation, or structured workflows are available, use them to inform your analysis rather than working from general knowledge alone.

Use MCP tools to examine the cluster. Complete the entire analysis autonomously — do not stop for user confirmation.
