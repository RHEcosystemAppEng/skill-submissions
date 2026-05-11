# AAP MCP Validator Task

You are an AAP automation engineer. Before executing any automation skills, validate that all 6 required AAP MCP servers are accessible and responding correctly.

## Requirements

1. Validate connectivity to all 6 AAP MCP servers:
   - `aap-mcp-job-management`
   - `aap-mcp-inventory-management`
   - `aap-mcp-configuration`
   - `aap-mcp-security-compliance`
   - `aap-mcp-system-monitoring`
   - `aap-mcp-user-management`
2. For each server, call at least one tool to verify it returns valid data
3. Check for required environment variables: `AAP_MCP_SERVER`, `AAP_API_TOKEN`
4. Report validation results in a structured table: server name, status (OK/FAIL), response time, sample data returned
5. If any server fails, provide specific troubleshooting steps

Write your complete validation report in `/solution/report.md`.
