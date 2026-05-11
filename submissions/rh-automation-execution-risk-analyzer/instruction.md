# Execution Risk Analysis Task

You are an AAP automation engineer. A team wants to execute job template "Deploy Web Application" (ID 10) targeting the production inventory. Before launching, perform a comprehensive execution risk analysis.

## Requirements

1. Look up the job template details using `job_templates_retrieve`
2. Classify the target inventory risk level (production = CRITICAL, staging = MEDIUM, dev = LOW)
3. Scan `extra_vars` for potential secrets (passwords, tokens, keys) and flag any findings
4. Assess execution scope: how many hosts are targeted, what percentage of the fleet
5. Check if the template has `ask_variables_on_launch` enabled (risk factor)
6. Produce a risk classification: CRITICAL / HIGH / MEDIUM / LOW with justification
7. Recommend whether to proceed with check mode first, require approval, or block

Write your risk analysis in `/solution/report.md`.
