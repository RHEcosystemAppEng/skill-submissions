# VM Inventory Task

You are an OpenShift Virtualization administrator. Your team needs a complete inventory of every VM in the cluster for capacity planning and compliance reporting.

## Scenario
The cluster has VMs spread across multiple namespaces. Some are running, some stopped. You need to produce a structured inventory showing each VM's resources, operating system, network details, and health conditions.

## Requirements
- List every VM across all namespaces in a structured table format
- For each VM report: name, namespace, status, CPU/memory resources, guest OS, IP address, node placement
- Identify VMs with health issues or degraded conditions
- Summarize totals per namespace

Write the inventory report in `/solution/report.md`.

**Important**: Before starting, check whether this environment provides reference documentation, skills, or other resources that can guide your approach. If tools, documentation, or structured workflows are available, use them to inform your analysis rather than working from general knowledge alone.

Use MCP tools to gather VM data. Complete the entire analysis autonomously — do not stop for user confirmation.
