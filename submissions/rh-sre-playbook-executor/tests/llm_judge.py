import json
import os
import sys
import time
from pathlib import Path

try:
    from anthropic import Anthropic
except ImportError:
    print("ERROR: anthropic package not installed")
    sys.exit(1)

CRITERIA = [
    {
        "id": "dry_run_before_production",
        "file": "/solution/report.md",
        "question": "Does the report describe a dry-run (check mode) step BEFORE actual production execution, explaining that job_type 'check' simulates changes without applying them?",
        "reference": "A skilled report follows the SKILL workflow: Phase 3 dry-run with job_type 'check' before Phase 4 production run with job_type 'run'. An unskilled report jumps to execution without a dry-run step.",
    },
    {
        "id": "git_flow_mandatory",
        "file": "/solution/report.md",
        "question": "Does the report address Git Flow (commit/push/sync) as a prerequisite before launching jobs, explaining that AAP executes from the synced project and there's no playbook override at launch?",
        "reference": "A skilled report explains the MANDATORY Git Flow: write playbook to Git, commit, push, wait for project sync, then launch. Without this, AAP executes the wrong playbook. An unskilled report doesn't mention Git Flow or assumes the playbook can be overridden at launch.",
    },
    {
        "id": "aap_mcp_tool_usage",
        "file": "/solution/report.md",
        "question": "Does the report reference specific AAP MCP tools for the workflow (job_templates_list for finding templates, job_templates_launch_retrieve for launching, jobs_retrieve for monitoring)?",
        "reference": "A skilled report names the actual MCP tools used at each step: job_templates_list, job_templates_retrieve, job_templates_launch_retrieve, jobs_retrieve, jobs_job_host_summaries_list. An unskilled report speaks generically about 'running the playbook'.",
    },
    {
        "id": "human_in_the_loop",
        "file": "/solution/report.md",
        "question": "Does the report include explicit human confirmation gates before production execution, consistent with a HITL (human-in-the-loop) safety approach?",
        "reference": "A skilled report includes confirmation checkpoints: before Git push, before dry-run, and before production execution. It waits for explicit 'yes' or 'execute'. An unskilled report automates everything without human gates.",
    },
]

SYSTEM_PROMPT = (
    "You are an evaluator for a cloud operations benchmark. You will be given a "
    "file produced by an AI agent, a yes/no question about its contents, and a "
    "REFERENCE ANSWER that describes what a correct, skilled response looks like.\n\n"
    "Rules:\n"
    "- Answer ONLY with a JSON object: {\"pass\": true} or {\"pass\": false}\n"
    "- Base your answer strictly on what is written in the file content\n"
    "- Do not infer or assume knowledge the agent did not demonstrate\n"
    "- Use the REFERENCE ANSWER to calibrate what counts as a pass\n"
    "- Accept different phrasings that convey the SAME concept\n"
    "- Do NOT use your own general knowledge to fill gaps"
)


def judge_criterion(client, model, criterion):
    filepath = criterion["file"]
    if not Path(filepath).exists():
        return {"id": criterion["id"], "pass": False, "reason": "file not found"}
    content = Path(filepath).read_text()
    if len(content) > 50000:
        content = content[:50000] + "\n... (truncated)"
    reference = criterion.get("reference", "")
    ref_block = f"\n\n## Reference Answer\n{reference}" if reference else ""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=model, max_tokens=64, system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": (
                    f"## File: {filepath}\n\n```\n{content}\n```\n\n"
                    f"## Question\n{criterion['question']}{ref_block}"
                )}],
            )
            text = response.content[0].text.strip()
            if "{" in text:
                text = text[text.index("{"):text.rindex("}") + 1]
            result = json.loads(text)
            return {"id": criterion["id"], "pass": bool(result.get("pass", False))}
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
            else:
                return {"id": criterion["id"], "pass": False, "reason": str(e)}


def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    base_url = os.getenv("ANTHROPIC_BASE_URL")
    model = os.getenv("LLM_JUDGE_MODEL", "claude-haiku-4-5")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set, skipping LLM judge")
        json.dump({"criteria": [], "passed": 0, "total": 0, "score": 0.0},
                  open("/logs/verifier/llm_judge.json", "w"), indent=2)
        return
    client_kwargs = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url
    client = Anthropic(**client_kwargs)
    results = []
    print(f"=== LLM Judge: evaluating {len(CRITERIA)} criteria with {model} ===")
    for criterion in CRITERIA:
        print(f"  Evaluating: {criterion['id']} ...", end=" ", flush=True)
        result = judge_criterion(client, model, criterion)
        results.append(result)
        print("PASS" if result["pass"] else "FAIL")
    passed = sum(1 for r in results if r["pass"])
    total = len(results)
    score = round(passed / total, 4) if total > 0 else 0.0
    print(f"=== LLM Judge: {passed}/{total} criteria passed (score={score}) ===")
    Path("/logs/verifier/llm_judge.json").write_text(json.dumps(
        {"criteria": results, "passed": passed, "total": total, "score": score}, indent=2))


if __name__ == "__main__":
    main()
