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
        "id": "allocation_based_capacity",
        "file": "/solution/report.md",
        "question": "Does the report calculate node utilization percentages based on VM resource ALLOCATIONS (vCPUs, memory requests) vs node capacity, rather than using runtime metrics from nodes_top?",
        "reference": "A skilled report sums VM allocations (spec.domain.cpu, spec.domain.memory.guest) and divides by node capacity (status.capacity) to get utilization. An unskilled report uses nodes_top runtime usage, which shows low numbers for idle VMs and gives misleading rebalance decisions.",
    },
    {
        "id": "rwo_cold_only",
        "file": "/solution/report.md",
        "question": "Does the report identify that VMs with RWO (ReadWriteOnce) storage cannot be live migrated and must use cold migration?",
        "reference": "A skilled report checks PVC access modes and flags RWO as requiring cold migration (stop, move, start). An unskilled report attempts live migration on all VMs regardless of storage type, or doesn't check storage at all.",
    },
    {
        "id": "overcommit_detection",
        "file": "/solution/report.md",
        "question": "Does the report check whether any node would exceed 100% allocated capacity after rebalancing, and warn about overcommit if so?",
        "reference": "A skilled report calculates post-migration allocated capacity and warns if any node exceeds 100% (CPU throttling risk, memory eviction risk). An unskilled report moves VMs without verifying the target node can handle the additional allocations.",
    },
    {
        "id": "cold_migration_procedure",
        "file": "/solution/report.md",
        "question": "Does the report describe the correct cold migration procedure: stop VM, set nodeAffinity to target node, then start VM?",
        "reference": "A skilled report follows the correct cold migration sequence: stop the VM, update nodeAffinity in the VM spec to pin it to the target, then start it. An unskilled report either just restarts hoping for different placement or uses only kubectl drain.",
    },
    {
        "id": "migration_type_distinction",
        "file": "/solution/report.md",
        "question": "Does the report clearly distinguish between live migration (RWX, near-zero downtime) and cold migration (RWO, brief downtime) for different VMs?",
        "reference": "A skilled report assigns the correct migration type per VM based on storage access mode: live for RWX (VirtualMachineInstanceMigration), cold for RWO (stop/affinity/start). An unskilled report uses a single migration method for all VMs.",
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
