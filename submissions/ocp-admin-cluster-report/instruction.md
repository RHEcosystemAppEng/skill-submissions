# Cluster Report Task

You are an OpenShift cluster administrator. Your operations lead needs a comprehensive infrastructure health snapshot for the weekly review.

## Scenario
Your environment has multiple cluster contexts configured — some are OpenShift, some may be vanilla Kubernetes, and some may be unreachable. You must accurately classify each context and produce a structured report for the accessible OpenShift clusters.

## Requirements
- Discover all available cluster contexts
- Determine which contexts are OpenShift vs non-OpenShift vs unreachable
- For each accessible OpenShift cluster: report version, nodes, projects, and workload health
- Explicitly classify contexts that are not OpenShift or cannot be reached

Write the complete cluster report in `/solution/report.md`.

Use MCP tools to examine the clusters. If reference documentation or skills are available in this environment, consult them before beginning work. Complete the entire analysis autonomously — do not stop for user confirmation.
