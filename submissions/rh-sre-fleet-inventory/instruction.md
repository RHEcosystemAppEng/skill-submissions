# Fleet Inventory Task

You are a Red Hat SRE. Your manager has asked for a current snapshot of all RHEL systems in your managed fleet ahead of an upcoming compliance audit.

## Scenario
The compliance team needs to know exactly what systems you manage, their RHEL versions, patch levels, and any outstanding vulnerability exposure. Some systems in the fleet may not be reporting properly. There is a known critical CVE (CVE-2026-1234) that may affect part of the fleet.

## Requirements
- Query the fleet to enumerate all managed RHEL systems with their key attributes
- Determine each system's reporting freshness and flag any that are not actively checking in
- For the known CVE, determine the per-system vulnerability status
- Group and summarize the fleet by RHEL version, environment, and vulnerability exposure
- Recommend next steps for any systems that need attention

Document your methodology, findings, and fleet assessment in `/solution/report.md`.

Use MCP tools to query data. If reference documentation or skills are available in this environment, consult them before beginning work. Complete the entire analysis autonomously — do not stop for user confirmation.
