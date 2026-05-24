import json, os, sys, time
from pathlib import Path
try:
    from anthropic import Anthropic
except ImportError:
    sys.exit(1)

CRITERIA = [
    {
        "id": "dspa_setup",
        "file": "/solution/report.md",
        "question": "Does the report describe setting up or verifying a DSPA (DataSciencePipelinesApplication) CR in the target namespace as the pipeline server?",
        "reference": "The skill requires a DSPA CR as the pipeline server in RHOAI. This is a specific Custom Resource type that an unskilled agent would not know about."
    },
    {
        "id": "kfp2_pipeline_lifecycle",
        "file": "/solution/report.md",
        "question": "Does the report demonstrate Kubeflow Pipelines 2.0 lifecycle management including submitting pipeline runs from YAML, scheduling recurring runs with cron, and monitoring with step-level logs?",
        "reference": "The skill covers KFP 2.0 specific features: YAML-based run submission, ScheduledWorkflow for cron scheduling, step-level pod monitoring and logs. An unskilled agent gives generic pipeline advice."
    }
]

SYSTEM_PROMPT = (
    "You are an evaluator for a cloud operations benchmark. You will be given a "
    "file produced by an AI agent, a yes/no question about its contents, and a "
    "REFERENCE ANSWER.\n\nRules:\n"
    "- Answer ONLY with a JSON object: {\"pass\": true} or {\"pass\": false}\n"
    "- Base your answer strictly on what is written in the file content\n"
    "- Do not infer or assume knowledge the agent did not demonstrate"
)

def judge_criterion(client, model, criterion):
    filepath = criterion["file"]
    if not Path(filepath).exists():
        return {"id": criterion["id"], "pass": False, "reason": "file not found"}
    content = Path(filepath).read_text()
    if len(content) > 50000:
        content = content[:50000] + "\n... (truncated)"
    ref = criterion.get("reference", "")
    ref_block = f"\n\n## Reference Answer\n{ref}" if ref else ""
    for attempt in range(3):
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
            if attempt < 2: time.sleep(5 * (attempt + 1))
            else: return {"id": criterion["id"], "pass": False, "reason": str(e)}

def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    base_url = os.getenv("ANTHROPIC_BASE_URL")
    model = os.getenv("LLM_JUDGE_MODEL", "claude-haiku-4-5")
    if not api_key:
        json.dump({"criteria": [], "passed": 0, "total": 0, "score": 0.0},
                  open("/logs/verifier/llm_judge.json", "w"), indent=2)
        return
    kwargs = {"api_key": api_key}
    if base_url: kwargs["base_url"] = base_url
    client = Anthropic(**kwargs)
    results = []
    for c in CRITERIA:
        r = judge_criterion(client, model, c)
        results.append(r)
        print(f"  {c['id']}: {'PASS' if r['pass'] else 'FAIL'}")
    passed = sum(1 for r in results if r["pass"])
    total = len(results)
    score = round(passed / total, 4) if total > 0 else 0.0
    print(f"=== LLM Judge: {passed}/{total} (score={score}) ===")
    Path("/logs/verifier/llm_judge.json").write_text(json.dumps(
        {"criteria": results, "passed": passed, "total": total, "score": score}, indent=2))

if __name__ == "__main__":
    main()
