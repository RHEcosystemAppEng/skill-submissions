# Support Ticket Severity Task

You are a Red Hat IT support specialist. A customer needs to file support tickets for three different situations and wants to know the correct severity for each.

## Scenarios
1. **Production OCP cluster down**: Their production OpenShift 4.14 cluster is completely unresponsive. All workloads are offline. There is no workaround. Business operations are halted.
2. **RHEL server with unpatched Critical CVE**: Their production RHEL 9 server has CVE-2024-6387 (OpenSSH regreSSHion) unpatched. The server is still running normally but they are concerned about exploitation risk. They have not applied the mitigation yet.
3. **Dev AAP intermittent errors**: Their development Ansible Automation Platform instance shows intermittent UI errors when running job templates. Jobs still complete, but the UI occasionally shows 500 errors. This is a non-production environment.

## Requirements
- For each scenario, determine the correct support ticket severity (Sev 1-4) with clear reasoning
- Show the SLA response times for both Premium and Standard support tiers
- Include a filing tip for high-severity tickets
- List what information the customer should include in each ticket
- If a CVE is involved, look it up and factor its severity into the ticket severity recommendation

Write your complete severity assessment in `/solution/report.md`.

Use MCP tools for CVE lookups. If reference documentation or skills are available in this environment, consult them before beginning work.
