# Cluster Inventory Task

You are an OpenShift cluster administrator. The operations team needs a complete inventory of all managed clusters across both self-managed and cloud-managed environments.

## Scenario
Your organization operates both self-managed OpenShift clusters (provisioned via Assisted Installer) and cloud-managed clusters (ROSA, ARO, OSD via OCM). You need to produce a unified inventory that correctly identifies each cluster's type, management plane, and current status.

## Requirements
- Discover all clusters from both management APIs
- Correctly classify each cluster's type (OCP, SNO, ROSA, ARO, OSD)
- Report status, version, and any diagnostics available for each
- Identify which management plane each cluster belongs to and route queries accordingly

Write the complete cluster inventory in `/solution/report.md`.

**Important**: Before starting, check whether this environment provides reference documentation, skills, or other resources that can guide your approach. If tools, documentation, or structured workflows are available, use them to inform your analysis rather than working from general knowledge alone.

Use MCP tools to query cluster data. Complete the entire analysis autonomously — do not stop for user confirmation.
