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
  {"id": "playbook_from_tool", "file": "/solution/report.md", "question": "Does the report include actual Ansible playbook YAML content that appears to come from an MCP tool call (e.g., containing 'dnf', 'become: true', 'security: true', 'hosts: targeted_systems') rather than a generic conceptual description of what a playbook would look like?", "reference": "A skilled report includes specific playbook YAML returned by the create_vulnerability_playbook MCP tool, with exact markers like 'dnf', 'become: true', 'security: true', 'hosts: targeted_systems'. An unskilled report describes playbooks conceptually ('you would create a playbook that...') without these specific artifacts."},
  {"id": "fleet_enumeration", "file": "/solution/report.md", "question": "Does the report include specific fleet statistics (such as total system count of 63, or environment breakdowns like 30 production / 15 staging / 10 development) that could only come from querying an inventory API?", "reference": "A skilled report includes exact numbers from the mock fleet (63 total systems, 30 production, 15 staging, 10 development, 5 QA, 3 legacy) obtained by calling get_host_details. An unskilled report discusses systems generically without exact counts from the data source."},
  {"id": "non_remediable_flagged", "file": "/solution/report.md", "question": "Does the report identify that at least one CVE (specifically CVE-2024-22222) does not have automated remediation available, and handles this case differently from remediable CVEs?", "reference": "A skilled report identifies CVE-2024-22222 as having no automated remediation (remediation_available: False) and treats it differently — suggesting manual steps or flagging it. An unskilled report either misses this distinction or treats all CVEs identically."},
  {"id": "compliance_from_data", "file": "/solution/report.md", "question": "Does the report reference specific compliance frameworks (PCI, SOC2, HIPAA) with details that appear to come from structured data fields rather than generic compliance advice?", "reference": "A skilled report references PCI-DSS, SOC2, and HIPAA compliance impacts as returned by the mock MCP data (pci_impact, soc2_impact, hipaa_impact fields with specific deadlines). An unskilled report may mention compliance generically but without data-driven specifics."},
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
