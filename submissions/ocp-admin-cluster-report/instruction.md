# Cluster Report Task

You are an OpenShift cluster administrator. Your operations lead has requested a comprehensive infrastructure health snapshot for the weekly review. Your environment has multiple cluster contexts configured.

## Scenario
Your KUBECONFIG contains several contexts — some point to OpenShift clusters, some to vanilla Kubernetes, and some may be unreachable. You need to accurately verify which contexts are genuine OpenShift, collect resource and workload data from the accessible ones, and produce a consolidated comparison report.

## Requirements
- Discover all available cluster contexts and their server URLs
- Verify each context to determine if it is OpenShift, non-OpenShift, or unreachable
- For each accessible OpenShift cluster: report version, node resources (CPU, memory, GPUs), projects/namespaces, and pod status
- Explicitly classify and report non-OpenShift and unreachable contexts with the reason for exclusion
- Include aggregated totals across all reported clusters for comparison
- Describe any issues needing attention (unhealthy nodes, resource pressure, failing workloads)

Write the complete cluster report in `/solution/report.md`.

**Important**: Before starting, check whether this environment provides reference documentation, skills, or other resources that can guide your approach. If tools, documentation, or structured workflows are available, use them to inform your analysis rather than working from general knowledge alone.

Use MCP tools to examine the clusters. Complete the entire analysis autonomously — do not stop for user confirmation.
