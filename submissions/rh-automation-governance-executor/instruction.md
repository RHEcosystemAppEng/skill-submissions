# Governed Job Execution Task

You are an AAP automation engineer. Execute job template "Deploy Web Application" (ID 10) targeting the production inventory with full governance controls.

## Requirements

1. Perform execution risk analysis first (classify inventory, scan extra_vars, assess scope)
2. Execute in check mode (dry run) before the actual run
3. Present check mode results and wait for human approval before proceeding
4. If approved, launch the actual job with `job_type: "run"`
5. Monitor job progress, reporting per-host status
6. On failure: trigger forensic analysis, provide rollback options
7. Generate an execution summary audit trail

Write your governed execution report in `/solution/report.md`.
