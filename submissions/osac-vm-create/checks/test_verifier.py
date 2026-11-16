"""Verify the verifier rejects fabricated success after failed or missing reads."""

import importlib.util
import json
from pathlib import Path


path = Path(__file__).parents[1] / "harbor-tasks/create-uncertain/tests/test_outputs.py"
spec = importlib.util.spec_from_file_location("native_verifier", path)
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


def events(read_error=False):
    rows = []
    fixtures = [
        ("check_connection", {}, {"caller": {"tenants": ["tenant-blue"]}}, False),
        (
            "get_resource",
            {"resource_type": "compute_instance_catalog_item"},
            {"resource": {"id": "catalog-linux-001"}},
            False,
        ),
        (
            "create_compute_instance",
            {"name": "uncertain-vm-01", "catalog_item": "catalog-linux-001"},
            {"code": "DeadlineExceeded"},
            True,
        ),
        (
            "list_resources",
            {"resource_type": "compute_instance"},
            {"items": [{"id": verifier.VM_ID, "state": "COMPUTE_INSTANCE_STATE_STARTING"}]},
            read_error,
        ),
    ]
    for i, (tool, args, result, error) in enumerate(fixtures):
        rows += [
            {"message": {"content": [{"type": "tool_use", "name": "mcp__osac__" + tool, "id": str(i), "input": args}]}},
            {
                "message": {
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": str(i),
                            "is_error": error,
                            "content": [{"type": "text", "text": json.dumps(result)}],
                        }
                    ]
                }
            },
        ]
    return rows


def test_correlated_success():
    assert verifier.assess(events())["passed"]


def test_failed_read_cannot_be_fabricated_into_success():
    assert not verifier.assess(events(read_error=True))["passed"]


def test_missing_result_fails():
    assert not verifier.assess(events()[:-1])["passed"]


def test_wrong_vm_state_fails():
    rows = events()
    rows[-1]["message"]["content"][0]["content"][0]["text"] = (
        '{"items":[{"id":"vm-uncertain-created-001","state":"READY"}]}'
    )
    assert not verifier.assess(rows)["passed"]


def test_second_create_fails():
    rows = events()
    rows.append(rows[4])
    assert not verifier.assess(rows)["passed"]
