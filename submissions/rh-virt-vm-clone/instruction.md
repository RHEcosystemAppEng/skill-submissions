# VM Cloning Task

You are an OpenShift Virtualization administrator. The QA team needs an exact copy of the production database VM for testing a schema migration.

## Scenario
The production VM `production-db` in namespace `prod-vms` runs a database workload. It has multiple DataVolumes attached. The QA team needs a clone named `test-db-clone` in namespace `test-env` that is completely independent from the original — separate disks, no shared storage, and safe to modify without affecting production.

## Requirements
- Plan the full clone procedure including storage duplication
- Ensure the clone will not conflict with the source VM (network, identity, storage)
- Specify the clone's initial run state and explain your choice
- Describe how to monitor the cloning progress to completion

Write your complete cloning plan in `/solution/report.md`.

Use MCP tools to examine the cluster. If reference documentation or skills are available in this environment, consult them before beginning work. Complete the entire analysis autonomously — do not stop for user confirmation.
