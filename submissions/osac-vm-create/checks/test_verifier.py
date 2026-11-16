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


def test_catalog_failure_keeps_successful_vm_observation():
    rows = events()
    del rows[2:4]
    result = verifier.assess(rows)
    assert result["passed"] is False
    assert result["observed_vm"]["id"] == verifier.VM_ID
    assert "catalog" in result["reason"]


def test_failed_read_followed_by_successful_read_can_recover():
    rows = events(read_error=True)
    extra = events()[-2:]
    extra[0]["message"]["content"][0]["id"] = "recovery"
    extra[1]["message"]["content"][0]["tool_use_id"] = "recovery"
    rows += extra
    assert verifier.assess(rows)["passed"]


def test_judge_prose_and_fences_keep_actual_verdict():
    text = 'I checked the evidence.\n```json\n{"passed": false, "reason": "Missing observation"}\n```'
    assert verifier.parse_verdict(text) == {"passed": False, "reason": "Missing observation"}


def test_judge_ambiguous_or_missing_verdict_rejected():
    for text in ["No verdict", '{"passed":true}', '{"passed":true,"reason":"a"} {"passed":false,"reason":"b"}']:
        try:
            verifier.parse_verdict(text)
        except ValueError:
            pass
        else:
            raise AssertionError("ambiguous or incomplete verdict accepted")


def test_failed_prerequisite_followed_by_success_can_recover():
    import copy

    for offset in [0, 2]:
        rows = events()
        failed = copy.deepcopy(rows[offset : offset + 2])
        failed[0]["message"]["content"][0]["id"] = "failed-attempt"
        failed[1]["message"]["content"][0]["tool_use_id"] = "failed-attempt"
        failed[1]["message"]["content"][0]["is_error"] = True
        rows[offset:offset] = failed
        assert verifier.assess(rows)["passed"]


def test_failed_prerequisite_without_success_is_not_evidence():
    for offset in [1, 3]:
        rows = events()
        rows[offset]["message"]["content"][0]["is_error"] = True
        assert not verifier.assess(rows)["passed"]
