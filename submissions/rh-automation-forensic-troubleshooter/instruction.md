# Forensic Troubleshooting Task

You are an AAP automation engineer. Job #42 (template "CVE Remediation - Critical") has failed on 3 out of 30 production hosts. Perform a forensic analysis to determine the root cause and recommend resolution.

## Requirements

1. Use `jobs_retrieve` to get job details and status
2. Use `jobs_job_events_list` to extract failure events with timestamps, building a failure timeline
3. Use `jobs_job_host_summaries_list` to identify which hosts failed and their error types
4. Correlate failures with host facts using inventory data (OS version, disk space, memory)
5. Classify the error type (connectivity, privilege escalation, package conflict, timeout, etc.)
6. Provide Red Hat documentation-backed resolution recommendations
7. Structure the report as: Event Timeline -> Host Correlation -> Error Classification -> Root Cause -> Resolution

Write your forensic analysis in `/solution/report.md`.
