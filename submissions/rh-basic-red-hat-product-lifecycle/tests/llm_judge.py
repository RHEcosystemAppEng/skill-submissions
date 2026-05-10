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
        "id": "backporting_model_explanation",
        "file": "/solution/report.md",
        "question": (
            "Does the report explain Red Hat's backporting model — that Red Hat "
            "backports security fixes into the shipped package version rather than "
            "rebasing to upstream, and that a higher release counter (e.g., -7.el8 "
            "to -8.el8) with the same version means a fix was applied?"
        ),
        "reference": (
            "A skilled report explains: Red Hat backports fixes into the shipped "
            "version (e.g., openssl-1.1.1k) rather than rebasing to upstream 3.x. "
            "The package format is name-version-release.elX where the release counter "
            "increments for each backported fix. Same version + higher release = fix "
            "applied. Version numbers look 'old' but carry all critical/important CVE "
            "fixes. An unskilled report says 'upgrade to latest OpenSSL' or does not "
            "explain why the version appears outdated."
        ),
    },
    {
        "id": "lifecycle_with_concrete_dates",
        "file": "/solution/report.md",
        "question": (
            "Does the report provide concrete lifecycle dates for RHEL 8 and "
            "OpenShift 4.14, distinguishing Full Support and Maintenance Support "
            "phases, and giving specific date-based recommendations?"
        ),
        "reference": (
            "A skilled report states dates concretely (e.g., 'Full Support ends May "
            "2024', 'Maintenance Support ends May 2029') rather than relatively. It "
            "distinguishes what updates each phase receives: Full Support = security + "
            "bugs + hardware enablement + minor releases; Maintenance Support = "
            "security + urgent bugs only. For OCP 4.14, it mentions 18-month lifecycle "
            "and EUS availability for even minors. An unskilled report gives vague "
            "guidance without specific dates or phase distinctions."
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
