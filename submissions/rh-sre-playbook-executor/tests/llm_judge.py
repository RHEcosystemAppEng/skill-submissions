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
        "id": "git_flow_before_launch",
        "file": "/solution/report.md",
        "question": "Does the report show Git Flow (write -> commit -> push -> sync complete) BEFORE launching any job, rather than launching directly from local files?",
        "reference": "A skilled report performs Git Flow before launch. An unskilled report launches directly or tries to override the playbook at launch time.",
    },
    {
        "id": "dry_run_check_mode",
        "file": "/solution/report.md",
        "question": "Does the report use job_type: 'check' for dry-run rather than CLI --check or skipping dry-run entirely?",
        "reference": "A skilled report uses job_type check in job_templates_launch_retrieve. An unskilled report either skips dry-run or uses CLI arguments.",
    },
    {
        "id": "job_polling",
        "file": "/solution/report.md",
        "question": "Does the report use jobs_retrieve for polling and jobs_job_events_list for event details, rather than parsing stdout?",
        "reference": "A skilled report uses the correct MCP tools for job monitoring. An unskilled report parses stdout or checks once.",
    },
    {
        "id": "host_summaries",
        "file": "/solution/report.md",
        "question": "Does the report collect per-host results using jobs_job_host_summaries_list?",
        "reference": "A skilled report uses the host summaries API. An unskilled report parses console output for host results.",
    },
    {
        "id": "synced_project_requirement",
        "file": "/solution/report.md",
        "question": "Does the report mention that AAP runs from the synced project only — no playbook override at launch time?",
        "reference": "A skilled report knows AAP requires project sync. An unskilled report tries to override playbook content at launch.",
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
