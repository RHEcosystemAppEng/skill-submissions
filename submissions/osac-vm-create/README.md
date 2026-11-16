# OSAC VM create: native Harbor smoke

Run `harbor-tasks/create-uncertain` through the managed Harbor MCP profile.
The agent is Claude Code using the cluster Sonnet route. Only the treatment
receives the skill; both conditions receive the identical real documentation.
The separate mock simulates an accepted create followed by DeadlineExceeded.
The verifier checks the trace and asks a Sonnet judge to assess the final answer.

This first delivery is one case and one repetition per condition. It proves
integration, not skill uplift. The committed skill is recovered from
osac-ai-skills commit 3c1c53a; it is not the later lost temporary candidate.
No new reference guide or reference index was generated.

Root files retain intake compatibility; the native Harbor task is under
`harbor-tasks/create-uncertain`. Expected outcomes live only in `tests/` and
mock source; neither is staged into the agent workspace.

The task asks for verified current status and the common environment permits
necessary read-only checks without another confirmation. The verifier records
`task_completion`, `protocol_compliance`, and independent `answer_accuracy` in
`evaluation-breakdown.json`. The composite reward is 1 only when all three pass.
An honest unknown-outcome answer can pass accuracy while completion still fails.
The accuracy judge receives actual correlated MCP responses and no precomputed
verdict. Verified current state is not restricted to the fixture's STARTING
value, and equivalent empty optional inputs preserve server defaults. PostgreSQL
continues to store the composite reward; category details are archived artifacts.

An explicit named-skill loading diagnostic is a separate single-treatment run
and is excluded from benefit comparisons. The ordinary pair uses identical
prompts and documents, differing only in tenant skill availability.
