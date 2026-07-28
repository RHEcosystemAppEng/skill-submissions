import os

def test_output_exists():
    assert os.path.exists("/workspace/review.md") or os.path.exists("/workspace/findings.json")
