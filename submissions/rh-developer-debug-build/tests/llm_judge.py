#!/usr/bin/env python3
"""LLM-based semantic evaluation for rh-developer-debug-build."""

import json
import os
import sys

REPORT_PATH = "/solution/report.md"
LLM_JUDGE_OUTPUT = "/logs/verifier/llm_judge.json"

CRITERIA = [
    {
        "id": "python_s2i_entry_point_diagnosis",
        "question": (
            "Does the report correctly diagnose the api-service failure as a Python S2I "
            "entry point issue, identifying the startup sequence (app.sh -> gunicorn+APP_MODULE "
            "-> app.py) and recommending APP_MODULE=main:app plus adding gunicorn to "
            "requirements.txt?"
        ),
        "reference": (
            "A skilled report explains the S2I Python run script detection order: "
            "1) app.sh, 2) gunicorn with APP_MODULE, 3) app.py. Since main.py is the "
            "entry point (not app.py) and gunicorn is not installed, the fix is to add "
            "gunicorn to requirements.txt and set APP_MODULE=main:app in the BuildConfig. "
            "An unskilled report may suggest generic fixes like renaming the file or "
            "editing Dockerfile without understanding the S2I startup mechanism."
        ),
    },
    {
        "id": "s2i_assemble_customization",
        "question": (
            "Does the report explain how to create a custom .s2i/bin/assemble script "
            "to install system dependencies (like pg_config/libpq-devel) and chain it "
            "with the default assemble at /usr/libexec/s2i/assemble?"
        ),
        "reference": (
            "A skilled report shows creating .s2i/bin/assemble that runs system package "
            "installs (e.g. microdnf or dnf install postgresql-devel) before calling the "
            "original assemble script at /usr/libexec/s2i/assemble. It also mentions "
            "psycopg2-binary as the simpler alternative. An unskilled report only suggests "
            "Dockerfile changes or doesn't know the S2I extension mechanism."
        ),
    },
    {
        "id": "multi_issue_build_diagnosis",
        "question": (
            "Does the report correctly identify all three issues across the three namespaces: "
            "(1) api-platform: S2I entry point misconfiguration, "
            "(2) web-frontend: OOMKilled/exit code 137 with memory limit too low, "
            "(3) order-system: Service selector mismatch causing 503?"
        ),
        "reference": (
            "A skilled report systematically investigates all three namespaces, identifies "
            "each distinct root cause with evidence from logs/events, and provides targeted "
            "fixes for each. An unskilled report may only address one issue or provide "
            "generic troubleshooting without specific diagnosis."
        ),
    },
]


def evaluate():
    if not os.path.exists(REPORT_PATH):
        results = [{"id": c["id"], "passed": False, "reason": "Report not found"} for c in CRITERIA]
        with open(LLM_JUDGE_OUTPUT, "w") as f:
            json.dump({"criteria": results, "score": 0.0}, f, indent=2)
        print(f"=== LLM Judge: 0/{len(CRITERIA)} criteria passed (score=0.0) ===")
        return

    with open(REPORT_PATH) as f:
        report = f.read()

    try:
        from anthropic import Anthropic
    except ImportError:
        print("WARNING: anthropic package not available, skipping LLM judge")
        return

    client = Anthropic()
    results = []
    passed_count = 0

    print(f"=== LLM Judge: evaluating {len(CRITERIA)} criteria with claude-sonnet ===")

    for criterion in CRITERIA:
        prompt = (
            f"You are evaluating an agent's report on OpenShift build debugging.\n\n"
            f"## Report\n\n{report}\n\n"
            f"## Evaluation Question\n\n{criterion['question']}\n\n"
            f"## Reference Answer\n\n{criterion['reference']}\n\n"
            f"Answer PASS if the report adequately addresses the question, FAIL otherwise.\n"
            f"Respond with exactly one word: PASS or FAIL"
        )

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=10,
                messages=[{"role": "user", "content": prompt}],
            )
            answer = response.content[0].text.strip().upper()
            passed = "PASS" in answer
        except Exception as e:
            print(f"  WARNING: API call failed for {criterion['id']}: {e}")
            passed = False
            answer = "ERROR"

        results.append({"id": criterion["id"], "passed": passed, "reason": answer})
        if passed:
            passed_count += 1
        print(f"  Evaluating: {criterion['id']} ... {'PASS' if passed else 'FAIL'}")

    score = passed_count / len(CRITERIA) if CRITERIA else 0.0
    with open(LLM_JUDGE_OUTPUT, "w") as f:
        json.dump({"criteria": results, "score": score}, f, indent=2)

    print(f"=== LLM Judge: {passed_count}/{len(CRITERIA)} criteria passed (score={score:.4f}) ===")


if __name__ == "__main__":
    evaluate()
