# AAP Playbook Execution Task

You are an SRE tasked with executing a remediation playbook through Ansible Automation Platform (AAP). A playbook has been generated for CVE-2024-6387 targeting host `ip-172-31-32-201.ec2.internal` and you need to launch it, monitor it, and report on the results.

## Scenario
The security team has already generated a remediation playbook (`playbooks/remediation/remediation-CVE-2024-6387.yml`) for the OpenSSH vulnerability. You need to find the right job template in AAP, ensure the playbook is synced, run a dry-run first, then execute the full job, and collect results.

## Goal
Produce a complete execution report documenting: template selection, Git flow (if needed), dry-run results, full execution results, and per-host summaries.

Write the complete execution report in `/solution/report.md`.

Use MCP tools to interact with AAP. If reference documentation or skills are available in this environment, consult them before beginning work. Complete the entire analysis autonomously — do not stop for user confirmation.
