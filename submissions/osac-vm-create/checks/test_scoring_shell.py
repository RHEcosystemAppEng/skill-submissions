"""Exercise continuous scoring and fatal infrastructure boundaries without models."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SOURCE = Path(__file__).parents[1] / "harbor-tasks/create-uncertain/tests/test.sh"


@pytest.mark.parametrize(
    "case,reward",
    [
        ("pass", 1.0),
        ("task_partial", 5 / 6),
        ("protocol_partial", 5 / 6),
        ("judge_partial", 0.8),
        ("zero", 0.0),
        ("missing", None),
        ("missing_behavior", None),
        ("malformed", None),
        ("wrong_type", None),
        ("nan", None),
        ("infinity", None),
        ("negative", None),
        ("too_large", None),
        ("contradictory", None),
        ("bad_passed", None),
        ("raw_mismatch", None),
        ("wrong_version", None),
        ("bad_finding", None),
        ("deductions_mismatch", None),
        ("pytest_assertion", None),
        ("pytest_infra", None),
    ],
)
def test_shell_validates_continuous_assessments_and_rejects_incomplete_runs(
    tmp_path, case, reward
):
    logs = tmp_path / "verifier"
    logs.mkdir()
    for name in (
        "reward.txt",
        "evaluation-breakdown.json",
        "behavior.json",
        "answer-judge.json",
        "answer-judge-raw.txt",
        "llm-judge-input.json",
    ):
        (logs / name).write_text("stale output must never count")
    script = tmp_path / "test.sh"
    script.write_text(
        SOURCE.read_text()
        .replace("/logs/verifier", str(logs))
        .replace("/tests/test_outputs.py", str(SOURCE.with_name("test_outputs.py")))
    )
    binary = tmp_path / "bin"
    binary.mkdir()
    shim = binary / "python"
    shim.write_text(
        f"#!{sys.executable}\n"
        + """import json, os, sys
from pathlib import Path
if sys.argv[1:3] != ['-m', 'pytest']:
    os.execv(sys.executable, [sys.executable, *sys.argv[1:]])
root = Path(os.environ['SCORING_LOG_ROOT'])
case = os.environ['SCORING_CASE']
def category(partial):
    checks = {'first': case != 'zero', 'second': case != 'zero' and not partial}
    score = sum(checks.values()) / len(checks)
    return {'score': score, 'passed': score == 1, 'checks': checks}
task, protocol = category(case == 'task_partial'), category(case == 'protocol_partial')
behavior = {'scoring_version': 2, 'task_completion': task, 'protocol_compliance': protocol,
            'score': (task['score'] + protocol['score']) / 2,
            'passed': task['passed'] and protocol['passed'], 'failures': []}
if case == 'contradictory': behavior['task_completion']['score'] = 0.6
if case == 'bad_passed': behavior['passed'] = False
if case == 'wrong_version': behavior['scoring_version'] = 3
if case != 'missing_behavior': (root / 'behavior.json').write_text(json.dumps(behavior))
score = 0 if case == 'zero' else 0.4 if case == 'judge_partial' else 1
score = {'wrong_type': True, 'nan': float('nan'), 'infinity': float('inf'), 'negative': -0.1, 'too_large': 1.1}.get(case, score)
findings = [] if score == 1 else [{'issue': 'Meaningful gap', 'evidence': 'Observed incomplete result', 'deduction': 1 - score}]
if case == 'bad_finding': score, findings = 0.5, [{'issue': 'Gap', 'evidence': 'trace', 'deduction': True}]
if case == 'deductions_mismatch': score, findings = 0.95, [{'issue': 'Gap', 'evidence': 'trace', 'deduction': 0.7}]
raw = {'score': score, 'reason': 'Fixture evidence-grounded judgment', 'findings': findings}
judgment = {'scoring_version': 2, 'passed': score == 1, **raw}
if case != 'missing':
    (root / 'answer-judge.json').write_text(json.dumps(judgment))
    if case == 'raw_mismatch': raw = {'score': 0.4, 'reason': 'Different score', 'findings': [{'issue':'gap','evidence':'trace','deduction':0.6}]}
    (root / 'answer-judge-raw.txt').write_text('{' if case == 'malformed' else json.dumps(raw))
if case == 'pytest_assertion': sys.exit(1)
if case == 'pytest_infra': sys.exit(2)
sys.exit(0)
"""
    )
    shim.chmod(0o755)
    run = subprocess.run(
        ["bash", str(script)],
        env={
            **os.environ,
            "PATH": str(binary) + os.pathsep + os.environ["PATH"],
            "SCORING_LOG_ROOT": str(logs),
            "SCORING_CASE": case,
        },
        capture_output=True,
        text=True,
    )
    if reward is None:
        assert run.returncode != 0
        assert not (logs / "reward.txt").exists()
        assert not (logs / "evaluation-breakdown.json").exists()
    else:
        assert run.returncode == 0, run.stderr
        assert float((logs / "reward.txt").read_text()) == pytest.approx(reward)
        result = json.loads((logs / "evaluation-breakdown.json").read_text())
        assert result["scoring_version"] == 2
        assert result["overall_score"] == pytest.approx(reward)
        assert result["overall_passed"] is (reward == 1)
        assert result["weights"] == {
            k: 1 / 3 for k in ("task_completion", "protocol_compliance", "llm_judgment")
        }
