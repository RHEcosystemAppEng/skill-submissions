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
  {"id": "advisory_based_gate", "file": "/solution/report.md", "question": "Does the report gate on CVE remediation availability using Red Hat advisory indicators (such as advisory_available, RHSA errata, advisories_list, or security advisories) rather than just generically asking 'is a fix available'?", "reference": "A skilled report specifically references Red Hat advisory indicators (RHSA, advisory_available, errata, advisories_list) as the mechanism for determining whether automated remediation exists. An unskilled report either skips this gate entirely or uses only generic language like 'check if a patch exists' without referencing the Red Hat advisory system."},
  {"id": "three_response_options", "file": "/solution/report.md", "question": "Does the report offer exactly three distinct response options at the execution confirmation point: (1) proceed/yes, (2) dry-run only, and (3) abort/cancel?", "reference": "A skilled report offers three explicit choices before execution: proceed (run the playbook), dry-run only (check mode without changes), and abort (cancel remediation). An unskilled report offers at most two options (proceed/cancel) or no structured confirmation options at all."},
  {"id": "mcp_tool_names", "file": "/solution/report.md", "question": "Does the report reference specific MCP tool names like get_cve, create_vulnerability_playbook, or explain_cves as part of the remediation workflow?", "reference": "A skilled report mentions specific Lightspeed MCP tool names (get_cve for CVE validation, create_vulnerability_playbook for playbook generation, explain_cves for system-level analysis) because the skill teaches these tools. An unskilled report describes remediation steps generically without naming specific API tools."},
  {"id": "mcp_validation_step", "file": "/solution/report.md", "question": "Does the report include a step to validate MCP server or tool availability (such as Lightspeed MCP or AAP MCP) as a prerequisite before starting CVE operations?", "reference": "A skilled report includes an explicit prerequisite validation step (Step 0) to verify that MCP servers (Lightspeed, AAP) are available and operational before beginning any CVE analysis or remediation. An unskilled report jumps straight into CVE analysis without verifying tool prerequisites."},
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
