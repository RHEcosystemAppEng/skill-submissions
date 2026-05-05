# VM Inventory Task

You are an OpenShift Virtualization administrator. Your team needs a complete picture of every VM in the cluster for capacity planning and compliance reporting.

## Requirements
- List every VM across all namespaces, organized in a clear, structured format
- For each VM report: name, namespace, status (Running/Stopped/Paused), CPU and memory allocation, operating system, and IP address if running
- Distinguish between the VM definition (desired state) and the runtime instance (actual state) where relevant
- Identify any VMs with issues: stopped unexpectedly, guest agent not responding, degraded conditions, or running end-of-life operating systems
- Summarize totals: how many VMs per namespace, how many running vs stopped, total resource allocation

Write the inventory report in `/solution/report.md`.

Use MCP tools to gather VM data. If reference documentation or skills are available in this environment, consult them before beginning work. Complete the entire analysis autonomously — do not stop to ask for user confirmation or input at any checkpoint.
