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
        "id": "sno_platform_none",
        "file": "/solution/report.md",
        "question": "Does the report specify platform: 'none' for the SNO cluster creation?",
        "reference": "A skilled report sets platform to 'none' for Single Node OpenShift. This is a Red Hat API requirement specific to SNO. An unskilled report uses 'baremetal' or 'vsphere' for SNO.",
    },
    {
        "id": "create_cluster_tool",
        "file": "/solution/report.md",
        "question": "Does the report reference the create_cluster MCP tool with parameters like name, version, base_domain, single_node?",
        "reference": "A skilled report uses create_cluster with specific parameters. An unskilled report uses generic API calls or doesn't specify the exact tool.",
    },
    {
        "id": "set_host_role",
        "file": "/solution/report.md",
        "question": "Does the report reference set_host_role with role values 'master' and/or 'worker'?",
        "reference": "A skilled report uses set_host_role with Assisted Installer role names: 'master' and 'worker'. An unskilled report uses Kubernetes terminology like 'control-plane'.",
    },
    {
        "id": "status_lifecycle",
        "file": "/solution/report.md",
        "question": "Does the report describe the cluster status lifecycle: waiting for 'ready' before install, then monitoring for 'installed' or 'error'?",
        "reference": "A skilled report monitors cluster status: 'ready' = can trigger install, 'installed' = success, 'error' = failure. An unskilled report doesn't describe the status lifecycle.",
    },
    {
        "id": "iso_discovery_workflow",
        "file": "/solution/report.md",
        "question": "Does the report describe the discovery ISO workflow: generating an ISO via cluster_iso_download_url, booting hosts from it, and waiting for host discovery?",
        "reference": "A skilled report describes the Assisted Installer's ISO-based discovery: generate ISO, boot bare metal hosts, wait for discovery. An unskilled report skips the ISO generation step or doesn't know about the host discovery process.",
    },
    {
        "id": "install_cluster_trigger",
        "file": "/solution/report.md",
        "question": "Does the report reference install_cluster as an explicit API call to trigger the installation after hosts are validated and cluster is ready?",
        "reference": "A skilled report calls install_cluster explicitly after readiness validation. An unskilled report assumes installation starts automatically or doesn't describe the trigger mechanism.",
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
