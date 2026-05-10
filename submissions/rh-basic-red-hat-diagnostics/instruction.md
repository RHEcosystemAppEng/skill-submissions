# Diagnostic Data Gathering Task

You are a Red Hat IT support specialist. A customer needs to collect diagnostic data for three separate support cases across different Red Hat products.

## Scenario
The customer has:
1. A **RHEL 9** server experiencing storage-related kernel errors — they need to collect diagnostics focused on storage subsystems
2. An **OpenShift Container Platform 4.14** cluster where pods in the `production` namespace are failing — they need a full cluster diagnostic bundle
3. An **Ansible Automation Platform 2.6** controller deployed as an **OCP operator** — the automation controller pods are crashing and they need AAP-specific diagnostics

## Requirements
- For each system, provide the exact commands to collect the appropriate diagnostic data
- Specify any product-version-specific details (e.g., correct container images, command flags)
- Include instructions for how to upload the resulting archives to Red Hat Support
- Warn the customer about sensitive data in diagnostic archives before sharing

Write your complete diagnostic guide in `/solution/report.md`.

If reference documentation or skills are available in this environment, consult them before beginning work.
