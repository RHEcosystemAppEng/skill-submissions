# Red Hat Security MCP Setup Task

You are helping a developer add the Red Hat Security MCP server to their project for live CVE and advisory data lookups.

## Requirements

1. Locate or create the project's `.mcp.json` file at the project root (use `git rev-parse --show-toplevel` to find it)
2. Add the `red-hat-security` server entry with HTTP transport type pointing to `https://security-mcp.api.redhat.com/mcp`
3. If `.mcp.json` already exists, merge the new server entry WITHOUT removing existing servers
4. Explain the Red Hat Customer Portal SSO browser login authentication flow
5. Note that no `headers` or `env` auth fields should be added - the server handles authentication via browser SSO
6. Recommend restarting the agentic tool or reloading MCP servers

Write your complete report in `/solution/report.md`.
