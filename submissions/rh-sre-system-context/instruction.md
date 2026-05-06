# System Context Task

You are a Red Hat SRE. A high-severity CVE has been identified that affects your fleet. Before applying any remediation, you need to gather comprehensive context about the affected systems.

## Scenario
CVE-2026-1234 has been flagged as critical. Your fleet includes a mix of bare-metal servers, VMs, and Kubernetes nodes across production, staging, and development environments. Some systems are RHEL 8, others RHEL 9. You need to understand the deployment landscape before creating a remediation plan.

## Requirements
- Identify all systems affected by the CVE using available MCP tools
- For each system, gather detailed context including OS version, infrastructure type, role, and environment
- Classify systems to determine remediation priority and ordering
- Assess reboot and service restart requirements after patching
- For Kubernetes nodes, identify workload safety considerations
- Recommend a remediation strategy (batch vs rolling, ordering, maintenance windows)

Document your system context analysis and remediation strategy in `/solution/report.md`.

Use MCP tools to query systems. If reference documentation or skills are available in this environment, consult them before beginning work. Complete the entire analysis autonomously — do not stop for user confirmation.
