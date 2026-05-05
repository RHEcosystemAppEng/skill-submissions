# VM Snapshot Creation Task

You are an OpenShift Virtualization administrator. Create a snapshot of VM `production-db` in namespace `prod-vms`.

## Requirements
- **Prerequisites**: Verify the cluster supports snapshots (VolumeSnapshotClass exists for the CSI driver). Check whether the QEMU guest agent is running on the VM to determine if application-consistent snapshots are possible, or only crash-consistent.
- **Hot-plug check**: Determine if the VM has any hot-plugged volumes, as these can block snapshot creation.
- **Snapshot specification**: Define the VirtualMachineSnapshot CR with the correct apiVersion, kind, and spec.source referencing the target VM.
- **Consistency levels**: Explain the difference between application-consistent (quiesce/freeze via guest agent) and crash-consistent snapshots. Document which level applies to this VM and why.
- **Monitoring**: Describe how to monitor snapshot progress — status phases (InProgress, Succeeded, Failed), readyToUse indicator, and status.indications fields.
- **Failure modes**: Document what can go wrong (storage full, guest agent not responding, hot-plug blockers) and how to handle each.

Use MCP tools to examine the cluster. Work autonomously — do not wait for user confirmation at any step. Document your methodology, findings, and snapshot plan in `/solution/report.md`.

If reference documentation or skills are available in this environment, consult them before beginning work.
