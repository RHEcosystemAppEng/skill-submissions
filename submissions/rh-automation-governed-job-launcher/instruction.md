# Governed Job Launch Task

You are an AAP automation engineer. After the execution-risk-analyzer classified the deployment as HIGH risk, execute the job template "CVE Remediation - Critical" (ID 11) with full governance controls.

## Requirements

1. Acknowledge that this skill requires prior execution-risk-analyzer results (CRITICAL/HIGH risk targets need extra controls)
2. Execute in **check mode** first using `job_templates_launch_retrieve` with `job_type: "check"`
3. Present check mode results and ask for human approval before actual execution
4. If approved, launch with `job_type: "run"` and monitor using `jobs_retrieve` polling
5. Track per-host execution status using `jobs_job_host_summaries_list`
6. If any host fails, provide rollback options:
   - Relaunch on failed hosts only using `jobs_relaunch_retrieve`
   - Full rollback using a designated rollback template
7. Report execution events from `jobs_job_events_list`

Write your governed execution report in `/solution/report.md`.
