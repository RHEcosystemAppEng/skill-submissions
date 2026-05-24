# Job Failure Analysis Task

You are an AAP automation engineer. Job #42 (template "CVE Remediation - Critical") has failed. Analyze the failure to classify the error type and reconstruct the failure timeline.

## Requirements

1. Use `jobs_retrieve` to get the job details, status, and execution time
2. Use `jobs_job_events_list` to extract ALL failure events with timestamps
3. Use `jobs_job_host_summaries_list` to identify which hosts failed and which succeeded
4. Use `jobs_stdout_retrieve` to get the raw job output for error messages
5. Reconstruct a failure timeline: when did each event occur relative to job start
6. Classify the error type: connectivity, privilege escalation, package conflict, timeout, playbook syntax, etc.
7. Identify the specific Ansible task and module that failed
8. List affected hosts with their specific error messages

Write your failure analysis in `/solution/report.md`.
