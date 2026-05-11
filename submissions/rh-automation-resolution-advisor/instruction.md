# Resolution Advisory Task

You are an AAP automation engineer. After failure analysis classified the error as a "privilege escalation timeout" on 3 production RHEL 8 hosts, provide Red Hat documentation-backed resolution recommendations.

## Requirements

1. Based on the classified error type "privilege escalation timeout", provide specific resolution steps
2. Reference Red Hat documentation (KB articles, AAP admin guides) for the resolution
3. Distinguish between:
   - Immediate fix: what to do right now to restore service
   - Root cause fix: configuration change to prevent recurrence
   - Preventive measure: monitoring or policy changes
4. If this is a known AAP issue, reference the specific KB article or bug
5. Provide Ansible-specific guidance: relevant module parameters, become settings, timeout configurations
6. Include verification steps to confirm the resolution worked
7. Assess whether re-execution is safe after applying the fix

Write your resolution advisory in `/solution/report.md`.
