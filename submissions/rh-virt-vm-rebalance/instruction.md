# VM Rebalancing Task

You are an OpenShift Virtualization administrator. Node `hv-prod-dc1-02` is overloaded and you need to rebalance its VM workloads across the cluster.

## Scenario
The cluster has 4 worker nodes. Node `hv-prod-dc1-02` hosts 5 VMs and is running at high utilization. Some VMs use RWX (ReadWriteMany) storage and some use RWO (ReadWriteOnce) storage. You need to produce a migration plan that moves VMs to less loaded nodes.

## Requirements
- Assess node capacity and determine which VMs should be migrated
- For each VM, determine the correct migration method and explain why
- Calculate projected node utilization after rebalancing, explaining which metrics you used and how you computed the percentages
- Identify any VMs that cannot be live migrated and explain what constraints apply
- Flag any risks (overcommit, storage limitations, concurrent migration limits)

Write your complete rebalancing plan and methodology in `/solution/report.md`.

Use MCP tools to examine the cluster. If reference documentation or skills are available in this environment, consult them before beginning work. Complete the entire analysis autonomously — do not stop for user confirmation.
