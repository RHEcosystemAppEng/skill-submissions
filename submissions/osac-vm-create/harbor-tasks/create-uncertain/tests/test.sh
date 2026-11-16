#!/bin/bash
set +e
python -m pytest /tests/test_outputs.py -v
verdict=$?
mkdir -p /logs/verifier
if [ "$verdict" -eq 0 ]; then echo 1 > /logs/verifier/reward.txt; else echo 0 > /logs/verifier/reward.txt; fi
exit 0
