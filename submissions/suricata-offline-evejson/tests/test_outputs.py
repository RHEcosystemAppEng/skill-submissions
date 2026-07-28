import os

def test_output_exists():
    assert os.path.exists("/workspace/results.json") or os.path.exists("/workspace/alerts.json")
