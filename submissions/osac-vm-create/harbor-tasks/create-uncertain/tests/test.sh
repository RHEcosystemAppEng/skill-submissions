#!/bin/bash
set +e
mkdir -p /logs/verifier
rm -f /logs/verifier/reward.txt /logs/verifier/evaluation-breakdown.json /logs/verifier/behavior.json /logs/verifier/answer-judge.json /logs/verifier/answer-judge-raw.txt /logs/verifier/llm-judge-input.json
python -m pytest /tests/test_outputs.py -v
verifier_exit=$?
VERIFIER_EXIT="$verifier_exit" python - <<'PYCODE'
import json
import math
import os
import runpy
from pathlib import Path
root = Path('/logs/verifier')
assert int(os.environ['VERIFIER_EXIT']) == 0, 'Incomplete evaluation: verifier infrastructure failed'
module = runpy.run_path('/tests/test_outputs.py')
valid_score = module['valid_score']
behavior = json.loads((root / 'behavior.json').read_text())
judgment = json.loads((root / 'answer-judge.json').read_text())
assert type(behavior['scoring_version']) is int and behavior['scoring_version'] == judgment['scoring_version'] == 2
assert judgment == module['parse_verdict']((root / 'answer-judge-raw.txt').read_text()), 'Raw/persisted judge disagree'
for category in ['task_completion', 'protocol_compliance']:
    item = behavior[category]
    assert isinstance(item['checks'], dict) and item['checks']
    assert all(type(v) is bool for v in item['checks'].values())
    assert valid_score(item['score'])
    assert math.isclose(item['score'], sum(item['checks'].values()) / len(item['checks']), rel_tol=0, abs_tol=1e-12)
    assert type(item['passed']) is bool and item['passed'] == (item['score'] == 1)
assert valid_score(behavior['score'])
assert math.isclose(behavior['score'], (behavior['task_completion']['score'] + behavior['protocol_compliance']['score']) / 2, rel_tol=0, abs_tol=1e-12)
assert type(behavior['passed']) is bool and behavior['passed'] == (behavior['score'] == 1)
assert isinstance(behavior['failures'], list)
overall = (behavior['task_completion']['score'] + behavior['protocol_compliance']['score'] + judgment['score']) / 3
weights = {k: 1 / 3 for k in ['task_completion', 'protocol_compliance', 'llm_judgment']}
breakdown = {
    'scoring_version': 2,
    'weights': weights,
    'task_completion': behavior['task_completion'],
    'protocol_compliance': behavior['protocol_compliance'],
    'llm_judgment': judgment,
    'failures': behavior['failures'],
    'overall_score': overall,
    'overall_passed': overall == 1,
}
(root / 'evaluation-breakdown.json').write_text(json.dumps(breakdown, indent=2, allow_nan=False))
(root / 'reward.txt').write_text(str(overall) + '\n')
PYCODE
breakdown_exit=$?
if [ "$breakdown_exit" -ne 0 ]; then exit "$breakdown_exit"; fi
exit 0
