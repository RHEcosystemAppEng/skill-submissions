# Host Fact Inspection Task

You are an AAP automation engineer. After job failure analysis identified hosts `web-prod-01` and `web-prod-03` as failed, correlate the failures with host system facts.

## Requirements

1. Use inventory management MCP tools to retrieve host details and variables
2. Check host system facts: OS version, kernel version, disk space, memory, CPU
3. Identify platform drift: are failed hosts running different OS versions or configurations than healthy hosts?
4. Check for resource exhaustion: disk space < 10%, memory pressure, swap usage
5. Correlate host facts with the specific failure type from the job failure analyzer
6. Present findings in a comparison table: failed hosts vs. healthy hosts
7. Determine if the failure is host-specific (platform drift/resources) or job-specific (configuration error)

Write your host fact analysis in `/solution/report.md`.
