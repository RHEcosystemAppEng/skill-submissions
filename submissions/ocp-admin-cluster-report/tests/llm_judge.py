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
        "id": "cluster_version_gvk",
        "file": "/solution/report.md",
        "question": "Does the report reference the ClusterVersion resource from the config.openshift.io API group as the method for verifying whether a context is OpenShift?",
        "reference": "A skilled report probes each context with resources_get for ClusterVersion (config.openshift.io/v1, name: version). An unskilled report uses ad-hoc checks like 'oc version' or guesses based on server URL.",
    },
    {
        "id": "error_classification",
        "file": "/solution/report.md",
        "question": "Does the report distinguish between 403 and 404 errors when probing for OpenShift, classifying 403 as 'OpenShift (unverified)' and 404 as 'non-OpenShift'?",
        "reference": "A skilled report: 403 on ClusterVersion = OpenShift with unknown version (include in report), 404 = not OpenShift (exclude by default). An unskilled report treats all probe errors the same way.",
    },
    {
        "id": "non_openshift_exclusion",
        "file": "/solution/report.md",
        "question": "Does the report explicitly exclude non-OpenShift contexts from the detailed cluster report, explaining why they are excluded?",
        "reference": "A skilled report classifies each context and excludes non-OpenShift contexts by default, explaining the classification. An unskilled report either includes everything without classification or silently skips contexts.",
    },
    {
        "id": "aggregated_totals",
        "file": "/solution/report.md",
        "question": "Does the report include aggregated totals across all clusters (total nodes, total CPU, total memory) in a comparison view?",
        "reference": "A skilled report includes a 'Total' row or summary aggregating resources across all reported clusters. An unskilled report lists each cluster independently without cross-cluster comparison.",
    },
    {
        "id": "gpu_inventory",
        "file": "/solution/report.md",
        "question": "Does the report include GPU information in the node resource inventory?",
        "reference": "A skilled report includes a GPU column in node/cluster resource tables. An unskilled report typically omits GPU data entirely.",
    },
    {
        "id": "verification_workflow",
        "file": "/solution/report.md",
        "question": "Does the report show a verification or discovery step where each context is classified before collecting detailed data?",
        "reference": "A skilled report starts with a 'Cluster Discovery' or 'Verification' section showing which contexts are OpenShift, non-OpenShift, or unreachable. An unskilled report jumps directly to querying resources without verification.",
    },
    {
        "id": "nodes_top_metrics",
        "file": "/solution/report.md",
        "question": "Does the report include actual CPU and memory utilization data (from nodes_top or Metrics Server) alongside static capacity, showing usage percentages?",
        "reference": "A skilled report uses nodes_top to show actual resource utilization (e.g., 'CPU: 4200m / 8000m = 52.5%'). An unskilled report only shows allocatable/capacity without runtime utilization data.",
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
