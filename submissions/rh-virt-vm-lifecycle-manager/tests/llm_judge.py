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
        "id": "stuck_vm_troubleshooting_depth",
        "file": "/solution/report.md",
        "question": (
            "Does the report troubleshoot the stuck web-frontend VM using "
            "specific diagnostic techniques from the lifecycle-errors.md "
            "troubleshooting documentation: checking finalizers on the VM "
            "object, verifying whether the VMI has a deletionTimestamp, "
            "checking virt-launcher pod status, and reviewing events — "
            "rather than just suggesting 'wait and retry' or 'force stop'?"
        ),
        "reference": (
            "A skilled report follows the lifecycle-errors.md diagnostic steps: "
            "(1) check .metadata.finalizers on the VM (kubevirt.io/virtualMachineControllerFinalize, "
            "foregroundDeletion), (2) check if VMI still exists and has deletionTimestamp, "
            "(3) check virt-launcher pod status using pods_list_in_namespace, "
            "(4) review events with events_list. It then provides specific remediation: "
            "force delete VMI, delete stuck virt-launcher pod, or remove finalizers "
            "as last resort. An unskilled report gives generic advice without "
            "the structured diagnostic approach."
        ),
    },
    {
        "id": "composite_restart_with_full_verification",
        "file": "/solution/report.md",
        "question": (
            "Does the report implement the production-db restart as separate "
            "stop and start operations with COMPLETE verification at each step: "
            "(1) stop via vm_lifecycle, (2) verify VMI is gone (NotFound), "
            "(3) wait a few seconds, (4) start via vm_lifecycle, "
            "(5) verify printableStatus is Running — and explicitly state "
            "that the restart action should NOT be used directly due to "
            "resourceVersion conflicts?"
        ),
        "reference": (
            "A skilled report follows the SKILL workflow: decompose restart "
            "into 5 explicit steps with verification between stop and start. "
            "It specifically warns against using action='restart' and explains "
            "that resourceVersion conflicts occur when start is issued too "
            "quickly after stop. The VMI must be confirmed gone (NotFound) — "
            "not just VM showing Stopped. An unskilled report may use a single "
            "restart command or skip intermediate VMI verification."
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
