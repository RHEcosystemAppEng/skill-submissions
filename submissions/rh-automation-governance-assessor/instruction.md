# AAP Governance Assessment Task

You are an AAP automation engineer. The security team needs a comprehensive governance readiness assessment before promoting the AAP platform to handle production workloads.

## Requirements

1. Assess all 7 governance domains + 1 bonus domain:
   - **Workflow Governance**: Approval gates, workflow coverage
   - **Notification Coverage**: Failure alerting, notification bindings
   - **Access Control / RBAC**: Teams, roles, least privilege
   - **Credential Security**: Separation of duties, credential hygiene
   - **Execution Environments**: Custom EEs, image provenance
   - **Workload Isolation**: Instance groups, capacity separation
   - **Audit Trail**: Activity stream, change tracking
   - **Bonus: External Authentication**: LDAP, SAML, SSO configuration
2. For each domain, use the appropriate AAP MCP tools to gather data
3. Score each domain (0-100%) with specific findings
4. Provide an overall governance readiness score with pass/fail recommendation
5. List specific remediation items ordered by priority

Write your governance assessment in `/solution/report.md`.
