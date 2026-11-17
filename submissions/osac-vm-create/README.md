# OSAC VM create: native Harbor smoke

Run `harbor-tasks/create-uncertain` through the managed Harbor MCP profile.
The agent is Claude Code using the cluster Sonnet route. Only the treatment
receives the skill; both conditions receive the identical real documentation.
The separate mock simulates an accepted create followed by DeadlineExceeded.
The verifier checks actions and asks a Sonnet judge to assess the full trajectory
and final answer.

This first delivery is one case and one repetition per condition. It proves
integration, not skill uplift. The committed skill is recovered from
osac-ai-skills commit 3c1c53a; it is not the later lost temporary candidate.
No new reference guide or reference index was generated.

Root files retain intake compatibility; the native Harbor task is under
`harbor-tasks/create-uncertain`. Expected outcomes live only in `tests/` and
mock source; neither is staged into the agent workspace.

The task asks for verified current status and the common environment permits
necessary read-only checks without another confirmation. The verifier writes
scoring version 2 to `evaluation-breakdown.json`. It reports
three continuous scores from 0 to 1, with explicit equal weights:

- `task_completion`: fraction of the five deterministic action checks satisfied.
- `protocol_compliance`: fraction of the four documented protocol checks satisfied.
- `llm_judgment`: Sonnet's evidence-grounded assessment of the **entire native
  trajectory and final result**, including decisions, recovery and all material
  claims. It deliberately overlaps the action checks as an independent review.

The native reward is the arithmetic mean of those three scores. A valid partial
score is a completed evaluation, not a pytest failure. The diagnostic `passed`
flags mean full credit (`score == 1`); they do not convert the reward to a binary
value or impose an additional AND gate. The surrounding generic report schema
may separately label any positive trial reward as passed; use the archived
numeric breakdown to distinguish that from full credit.

The judge receives the exact final task request and shared environment context
staged by trusted orchestration into `/tests/judge-context.json`, the complete
untruncated native trace and the full final result event. It receives no hidden
fixture values or deterministic verdicts. No local phrase/regex matcher decides
semantic correctness. Sonnet returns a numeric score, a reason and concrete
trace/result findings with positive deductions. Score must equal one minus the
sum of deductions (within 1e-6), so 1.0 requires no findings. Rubric anchors
range from no useful/safe completion (0) through partial progress (0.5) to fully
supported completion (1). Unsupported material scope, cause, timing or readiness
claims require deductions even when the core VM ID/state is correct.

`answer-judge.json` retains its filename for artifact compatibility but now holds
the scoring-v2 full-trace LLM judgment. `answer-judge-raw.txt` preserves its raw
response. `llm-judge-input.json` preserves the exact nonsecret request payload
(model, temperature and messages), without the authorization header or API key.
Provider failures, missing context/assessments, malformed or nonfinite/out-of-range
scores and contradictory scores/deductions fail infrastructure and produce no
valid reward. Trace/context is never silently clipped; provider context overflow
is an infrastructure failure. The shell clears stale output before each run and
validates raw-versus-parsed judgments and the complete scoring arithmetic.

Native trace verification accepts Claude Code's actual `claude-code.txt` and
Codex CLI's actual `codex.txt` JSONL output; it rejects ambiguous multiple native
traces. Codex MCP dispatches/results and shell commands are adapted internally
for the action checks. The original trace is never rewritten as Claude events.
The judge input records `native_trace_format`, preserves the entire original
trace and copies the actual final result event. Codex additionally requires a
completed turn and final agent-message event, with no terminal stream failure.
This adapter has unit coverage; local Codex execution is a separate validation
from the deployed Claude Code/Sonnet comparison and is not evidence of identical
agent/model behavior. ATIF conversion is not required for scoring.

The skill and reference documents are unchanged. Task status can be any verified
current state; empty optional inputs preserve server defaults. PostgreSQL stores
the numeric composite reward, while category/check details are archived. Earlier
binary-score archives remain unchanged and must not be merged with scoring-v2
results as though their scales were identical.

An explicit named-skill loading diagnostic is a separate single-treatment run
and is excluded from benefit comparisons. The ordinary pair uses identical
prompts and documents, differing only in tenant skill availability.
