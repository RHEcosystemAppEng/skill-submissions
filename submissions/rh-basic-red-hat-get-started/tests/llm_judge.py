import json, os, sys, time
from pathlib import Path
try:
    from anthropic import Anthropic
except ImportError:
    sys.exit(1)

CRITERIA = [
    {
        "id": "five_skills_listed",
        "file": "/solution/report.md",
        "question": "Does the report list all 5 Red Hat skills to install: red-hat-cve-explainer, red-hat-diagnostics, red-hat-product-lifecycle, red-hat-security-mcp-setup, and red-hat-support-severity?",
        "reference": "The installer SKILL.md defines exactly these 5 skills. A skilled agent lists all 5; an unskilled agent may not know these specific skill names.",
    },
    {
        "id": "self_destruct",
        "file": "/solution/report.md",
        "question": "Does the report mention the installer removing/deleting itself (self-destruct) after completing installation?",
        "reference": "The skill explicitly requires self-destruct: delete the installer's directory and tell the user 'This installer has removed itself.'",
    },
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
