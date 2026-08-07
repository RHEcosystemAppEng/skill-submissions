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
        "id": "dual_mcp_query",
        "file": "/solution/report.md",
        "question": "Does the report query both openshift-self-managed and openshift-ocm-managed MCP servers to discover all clusters?",
        "reference": "A skilled report queries both MCP servers to get the complete fleet. An unskilled report queries only one and misses clusters from the other management plane.",
    },
    {
        "id": "source_routing",
        "file": "/solution/report.md",
        "question": "Does the report use the cluster's 'source' field to route detail queries to the correct MCP server (ocm vs assisted-installer)?",
        "reference": "A skilled report checks the source field: 'ocm' routes to openshift-ocm-managed, 'assisted-installer' routes to openshift-self-managed. An unskilled report doesn't know the routing logic.",
    },
    {
        "id": "cloud_provider_classification",
        "file": "/solution/report.md",
        "question": "Does the report use cloud_provider.id to classify managed clusters as ROSA (aws), ARO (azure), or OSD (gcp)?",
        "reference": "A skilled report reads cloud_provider.id to determine: aws=ROSA, azure=ARO, gcp=OSD. An unskilled report doesn't distinguish between managed cluster flavors.",
    },
    {
        "id": "diagnostics_availability",
        "file": "/solution/report.md",
        "question": "Does the report mention that cluster_events and cluster_logs are only available for self-managed clusters, not ROSA/ARO/OSD?",
        "reference": "A skilled report notes that cluster_events and cluster_logs_download_url exist only on openshift-self-managed. An unskilled report tries these on all clusters.",
    },
    {
        "id": "list_clusters_tool",
        "file": "/solution/report.md",
        "question": "Does the report use the list_clusters MCP tool from both servers as the primary fleet discovery mechanism?",
        "reference": "A skilled report calls list_clusters on both openshift-self-managed and openshift-ocm-managed to get complete fleet data. An unskilled report uses kubectl or a single generic API call.",
    },
    {
        "id": "sno_detection",
        "file": "/solution/report.md",
        "question": "Does the report detect and classify SNO (Single Node OpenShift) clusters by checking platform and single_node fields?",
        "reference": "A skilled report identifies SNO clusters via platform='none' and single_node=true, classifying them separately from regular OCP multi-node clusters. An unskilled report groups SNO with regular OCP.",
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
