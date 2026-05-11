# Red Hat Skills Installer Task

You are setting up the Red Hat agent skills pack for a new project. Execute the bootstrap installer workflow.

## Requirements

1. Identify the SKILLS_REPO URL: `https://github.com/RHEcosystemAppEng/agentic-collections/tree/main/rh-basic/skills`
2. Download each of the 5 skills' SKILL.md files from the repo into the appropriate skills directory:
   - red-hat-cve-explainer
   - red-hat-diagnostics
   - red-hat-product-lifecycle
   - red-hat-security-mcp-setup
   - red-hat-support-severity
3. Handle any download failures gracefully: print the URL and target path, tell the user to download manually, then continue with the remaining skills
4. Generate a post-install summary listing all 5 available commands with their descriptions
5. After delivering the summary, perform self-destruct: delete the installer skill directory and confirm removal

Write your complete report in `/solution/report.md`.
