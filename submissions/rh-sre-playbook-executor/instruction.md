# Playbook Execution Task

You are a Red Hat SRE. A remediation playbook for CVE-2026-1234 has been generated and needs to be executed through Ansible Automation Platform (AAP).

## Scenario
The playbook file is `remediation-CVE-2026-1234.yml`. There is an existing job template in AAP called "CVE Remediation Template" but it currently points to a different playbook (`cve-remediation.yml`). You need to figure out how to execute your new playbook using this template, run a dry-run first, then execute for real, and handle any failures.

## Requirements
- Determine how to use the existing AAP job template to run your new playbook
- Plan the full execution: pre-flight, dry-run, production run, monitoring, and failure handling
- Explain what must happen before any job can be launched
- Document how to launch in dry-run (check) mode vs production mode
- Describe how to handle partial failures (some hosts succeed, some fail)

Write your complete execution plan in `/solution/report.md`.

Use MCP tools to interact with AAP. If reference documentation or skills are available in this environment, consult them before beginning work. Complete the entire analysis autonomously — do not stop for user confirmation.
