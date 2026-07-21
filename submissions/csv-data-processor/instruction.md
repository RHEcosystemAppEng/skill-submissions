Process the server metrics file at /supportive/server_metrics.csv:

1. Handle any missing values
2. Filter to only running servers
3. Group by region and calculate average CPU, total memory, and server count
4. Save the summary to /workspace/summary.csv
5. Write a report to /workspace/report.md
