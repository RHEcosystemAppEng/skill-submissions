# Governance Readiness Assessment Task

You are an AAP automation engineer. Perform a scoped governance readiness assessment focusing on Credential Security and RBAC domains for the AAP platform.

## Requirements

1. Validate all 6 AAP MCP servers are accessible first
2. Assess the **Credential Security** domain:
   - Check credential separation of duties
   - Verify credential hygiene (no shared credentials, rotation compliance)
   - Assess credential types used (machine, SCM, vault, cloud)
3. Assess the **Access Control / RBAC** domain:
   - Enumerate teams and roles
   - Verify least privilege principle
   - Check for admin role overuse
4. For each domain, provide a readiness score (0-100%)
5. Provide prioritized remediation items
6. Note that this assessment requires all 6 AAP MCP servers for a complete audit

Write your readiness assessment in `/solution/report.md`.
