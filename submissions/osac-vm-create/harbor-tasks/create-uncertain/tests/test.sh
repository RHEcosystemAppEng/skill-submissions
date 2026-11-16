#!/bin/bash
set +e
mkdir -p /logs/verifier
rm -f /logs/verifier/reward.txt /logs/verifier/evaluation-breakdown.json /logs/verifier/behavior.json /logs/verifier/answer-judge.json /logs/verifier/answer-judge-raw.txt
python -m pytest /tests/test_outputs.py -v
verifier_exit=$?
VERIFIER_EXIT="$verifier_exit" python - <<'PYCODE'
import json
import os
from pathlib import Path
root = Path('/logs/verifier')
behavior = json.loads((root / 'behavior.json').read_text())
answer = json.loads((root / 'answer-judge.json').read_text())
for category in ['task_completion', 'protocol_compliance']:
    item = behavior[category]
    assert type(item['passed']) is bool
    assert isinstance(item['checks'], dict) and item['checks']
    assert all(type(v) is bool for v in item['checks'].values())
    assert item['passed'] == all(item['checks'].values())
assert type(behavior['passed']) is bool and type(answer['passed']) is bool
assert isinstance(answer['reason'], str)
assert behavior['passed'] == (behavior['task_completion']['passed'] and behavior['protocol_compliance']['passed'])
assert isinstance(behavior['failures'], list)
overall = behavior['passed'] and answer['passed']
assert int(os.environ['VERIFIER_EXIT']) == (0 if overall else 1), 'Pytest status disagrees with completed assessments'
breakdown = {
    'task_completion': behavior['task_completion'],
    'protocol_compliance': behavior['protocol_compliance'],
    'answer_accuracy': answer,
    'failures': behavior['failures'],
    'overall_passed': overall,
}
(root / 'evaluation-breakdown.json').write_text(json.dumps(breakdown, indent=2))
(root / 'reward.txt').write_text('1\n' if overall else '0\n')
PYCODE
breakdown_exit=$?
if [ "$breakdown_exit" -ne 0 ]; then exit "$breakdown_exit"; fi
exit 0
