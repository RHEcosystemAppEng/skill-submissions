import os

def test_output_exists():
    assert os.path.exists("/workspace/routes.json") or os.path.exists("/workspace/solution.json")
