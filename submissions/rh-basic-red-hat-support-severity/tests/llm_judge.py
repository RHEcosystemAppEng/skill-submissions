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
        "id": "cve_severity_adjustment",
        "file": "/solution/report.md",
        "question": (
            "For the scenario of a production RHEL server with an unpatched Critical "
            "CVE (CVE-2024-6387) that is still running normally, does the report "
            "recommend Severity 2 (High) rather than Severity 3, and explain that a "
            "Critical CVE on unpatched production warrants escalation even when the "
            "system is not fully down?"
        ),
        "reference": (
            "A skilled report applies the CVE adjustment rule: a Critical or Important "
            "CVE with a known exploit on an unpatched production system that is not "
            "fully down should be Sev 2, not Sev 3. The reasoning connects the CVE "
            "severity (Critical, remote unauthenticated RCE) to the escalation from "
            "what would otherwise be Sev 3. An unskilled report rates this as Sev 3 "
            "(partial loss / workaround exists) without considering CVE severity."
        ),
    },
    {
        "id": "sla_premium_vs_standard",
        "file": "/solution/report.md",
        "question": (
            "Does the report present SLA response times for both Premium and Standard "
            "support tiers, with specific time values (e.g., Premium Sev 1 = 1 hour, "
            "Standard Sev 1 = 1 business hour)?"
        ),
        "reference": (
            "A skilled report shows a structured SLA table with Premium vs Standard "
            "response times: Sev 1 (Premium: 1 hour, Standard: 1 business hour), "
            "Sev 2 (Premium: 2 hours, Standard: 4 business hours), etc. It also "
            "notes 24x7 availability (Premium Sev 1: yes, Standard: business hours "
            "only). An unskilled report gives vague SLA guidance without specific "
            "times or tier distinction."
        ),
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
