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

Use MCP tools to gather VM data. If reference documentation or skills are available in this environment, consult them before beginning work. Complete the entire analysis autonomously — do not stop for user confirmation.
