# Job Template Creator Task

You are a Red Hat SRE. A remediation playbook for CVE-2026-1234 has been prepared and you need to create a job template in Ansible Automation Platform (AAP) so the operations team can execute it against affected production hosts.

## Scenario
The playbook `remediation-CVE-2026-1234.yml` is ready. There is an AAP instance available with projects, inventories, and credentials already configured. Your task is to set up a complete job template that the ops team can use to execute this playbook.

## Requirements
- Investigate the AAP environment to determine available projects, inventories, and credentials
- Create a plan for setting up the job template, including the exact method for creating it
- Specify all template configuration: name, playbook path, project, inventory, credentials, privilege escalation, and launch-time prompt settings
- Explain what must happen to the playbook file before the template can reference it
- Address how the template should handle flexibility at execution time (variables, host limiting, job type selection)

Write your complete plan and configuration in `/solution/report.md`.

Use MCP tools to query AAP. If reference documentation or skills are available in this environment, consult them before beginning work. Complete the entire analysis autonomously — do not stop for user confirmation.
