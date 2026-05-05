# CVE Remediation Workflow Task

You are a Red Hat SRE. A critical CVE has been reported and you need to plan and document a complete end-to-end remediation workflow, from initial validation through execution and verification.

## Scenario
CVE-2026-1234 (Critical, CVSS 9.8) has been identified as affecting production RHEL systems in your fleet. Management wants a comprehensive remediation plan that covers every phase of the response.

## Requirements
Your workflow plan must cover these phases in order, with decision gates between them:

1. **CVE Validation** — Confirm the CVE is real, assess severity, and determine whether automated remediation is available. If no remediation exists, document how to handle this (manual intervention, risk acceptance, etc.).
2. **Impact Assessment** — Identify which systems are affected and their criticality.
3. **System Context** — Understand each affected system's role, dependencies, and constraints before patching.
4. **Playbook Planning** — How the remediation playbook will be created or selected.
5. **Execution Planning** — How the playbook will be run: dry-run first, then production. Include approval gates and rollback strategy.
6. **Verification Planning** — How you will confirm remediation was successful after execution.

At each phase transition, describe the decision gate: what conditions must be met before proceeding, and what happens if the gate fails. Include an upfront planning checkpoint (before starting) and a pre-execution review checkpoint (after playbook is ready but before running it).

Document the complete workflow plan in `/solution/report.md`.

Use MCP tools to query data. If reference documentation or skills are available in this environment, consult them before beginning work. Complete the entire analysis autonomously — do not stop to ask for user confirmation or input at any checkpoint. Use reasonable defaults and proceed through every step to produce the final report.
