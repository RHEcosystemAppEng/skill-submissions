"""Execute the native scoring shell boundary without model/provider calls."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

SOURCE = Path(__file__).parents[1] / "harbor-tasks/create-uncertain/tests/test.sh"


@pytest.mark.parametrize(
    "case,reward,passed",
    [
        ("pass", "1", True),
        ("task_fail", "0", False),
        ("protocol_fail", "0", False),
        ("answer_fail", "0", False),
        ("missing", None, None),
        ("malformed", None, None),
        ("wrong_type", None, None),
        ("contradictory", None, None),
        ("pytest_infra", None, None),
    ],
)
def test_shell_requires_consistent_completed_assessments(
    tmp_path, case, reward, passed
):
    logs = tmp_path / "verifier"
    logs.mkdir()
    # Stale outputs must not make a failed current attempt look complete.
    (logs / "reward.txt").write_text("1")
    (logs / "evaluation-breakdown.json").write_text('{"overall_passed":true}')
    script = tmp_path / "test.sh"
    script.write_text(SOURCE.read_text().replace("/logs/verifier", str(logs)))
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
task, protocol, answer = case != 'task_fail', case != 'protocol_fail', case != 'answer_fail'
behavior = {
    'task_completion': {'passed': task, 'checks': {'observed': task}},
    'protocol_compliance': {'passed': protocol, 'checks': {'observed': protocol}},
    'passed': task and protocol,
    'failures': [],
}
(root / 'behavior.json').write_text(json.dumps(behavior))
if case != 'missing':
    verdict = {'passed': answer, 'reason': 'fixture evidence'}
    if case == 'wrong_type': verdict['passed'] = 'false'
    (root / 'answer-judge.json').write_text('{' if case == 'malformed' else json.dumps(verdict))
if case == 'pytest_infra': sys.exit(2)
if case == 'contradictory': sys.exit(1)
sys.exit(0 if task and protocol and answer else 1)
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
        import json

        assert run.returncode == 0, run.stderr
        assert (logs / "reward.txt").read_text().strip() == reward
        result = json.loads((logs / "evaluation-breakdown.json").read_text())
        assert result["overall_passed"] is passed
        if case in {"task_fail", "protocol_fail"}:
            assert result["answer_accuracy"]["passed"] is True
