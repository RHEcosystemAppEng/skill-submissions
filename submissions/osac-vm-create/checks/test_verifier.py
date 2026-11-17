"""Verify the verifier rejects fabricated success after failed or missing reads."""

import importlib.util
import json
from pathlib import Path

import pytest


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
            {
                "resource": {
                    "id": "catalog-linux-001",
                    "name": "standard-linux",
                    "state": "published",
                }
            },
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
            {
                "items": [
                    {
                        "id": verifier.VM_ID,
                        "name": "uncertain-vm-01",
                        "state": "COMPUTE_INSTANCE_STATE_STARTING",
                    }
                ]
            },
            read_error,
        ),
    ]
    for i, (tool, args, result, error) in enumerate(fixtures):
        rows += [
            {
                "message": {
                    "content": [
                        {
                            "type": "tool_use",
                            "name": "mcp__osac__" + tool,
                            "id": str(i),
                            "input": args,
                        }
                    ]
                }
            },
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


def test_successful_catalog_list_inspects_selected_published_record():
    rows = events()
    rows[2]["message"]["content"][0]["name"] = "mcp__osac__list_resources"
    resource = json.loads(rows[3]["message"]["content"][0]["content"][0]["text"])[
        "resource"
    ]
    rows[3]["message"]["content"][0]["content"][0]["text"] = json.dumps(
        {"items": [resource], "offset": 0, "size": 1, "total": 1}
    )
    assert verifier.assess(rows)["passed"]


@pytest.mark.parametrize(
    "content,error,resource_type,after_create",
    [
        (
            '{"items":[{"id":"another-catalog","name":"standard-linux","state":"published"}]}',
            False,
            "compute_instance_catalog_item",
            False,
        ),
        (
            '{"items":[{"id":"catalog-linux-001","name":"different-offering","state":"published"}]}',
            False,
            "compute_instance_catalog_item",
            False,
        ),
        (
            '{"items":[{"id":"catalog-linux-001","name":"standard-linux","state":"draft"}]}',
            False,
            "compute_instance_catalog_item",
            False,
        ),
        (
            '{"items":[{"id":"catalog-linux-001"},{"name":"standard-linux","state":"published"}]}',
            False,
            "compute_instance_catalog_item",
            False,
        ),
        (
            '{"items":[{"id":"catalog-linux-001","name":"standard-linux","state":"published"}]}',
            True,
            "compute_instance_catalog_item",
            False,
        ),
        (
            '{"items":[{"id":"catalog-linux-001","name":"standard-linux","state":"published"}]}',
            False,
            "compute_instance",
            False,
        ),
        (
            '{"items":[{"id":"catalog-linux-001","name":"standard-linux","state":"published"}]}',
            False,
            "compute_instance_catalog_item",
            True,
        ),
        ('{"items":', False, "compute_instance_catalog_item", False),
        ('{"items":[]}', False, "compute_instance_catalog_item", False),
    ],
)
def test_invalid_catalog_lists_do_not_prove_inspection(
    content, error, resource_type, after_create
):
    rows = events()
    call, result = rows[2:4]
    call["message"]["content"][0]["name"] = "mcp__osac__list_resources"
    call["message"]["content"][0]["input"]["resource_type"] = resource_type
    result["message"]["content"][0]["is_error"] = error
    result["message"]["content"][0]["content"][0]["text"] = content
    if after_create:
        del rows[2:4]
        rows[4:4] = [call, result]
    assert not verifier.assess(rows)["protocol_compliance"]["checks"][
        "catalog_inspected"
    ]


def test_failed_read_cannot_be_fabricated_into_success():
    assert not verifier.assess(events(read_error=True))["passed"]


def test_missing_result_fails():
    assert not verifier.assess(events()[:-1])["passed"]


def test_verified_current_state_is_not_restricted_to_fixture_starting():
    rows = events()
    rows[-1]["message"]["content"][0]["content"][0]["text"] = json.dumps(
        {"items": [{"id": verifier.VM_ID, "name": "uncertain-vm-01", "state": "READY"}]}
    )
    assert verifier.assess(rows)["task_completion"]["passed"]


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


def test_judge_prose_and_fences_keep_numeric_semantic_verdict():
    raw = {
        "score": 0.7,
        "reason": "Useful recovery with unsupported claims",
        "findings": [
            {
                "issue": "Unsupported scope",
                "evidence": "Visible tenants do not name the selected default",
                "deduction": 0.3,
            }
        ],
    }
    result = verifier.parse_verdict(
        "I reviewed the full trace.\n```json\n" + json.dumps(raw) + "\n```"
    )
    assert result == {**raw, "scoring_version": 2, "passed": False}


@pytest.mark.parametrize(
    "score",
    [True, False, float("nan"), float("inf"), -float("inf"), -0.1, 1.1, "0.5", None],
)
def test_judge_invalid_numeric_scores_rejected(score):
    with pytest.raises(ValueError):
        verifier.parse_verdict(
            json.dumps({"score": score, "reason": "reviewed", "findings": []})
        )


@pytest.mark.parametrize(
    "text",
    [
        "No assessment",
        '{"score":0.5}',
        '{"score":1,"reason":"a","findings":[]} {"score":1,"reason":"b","findings":[]}',
        '{"passed":true,"reason":"binary"}',
        '{"score":1,"reason":"full","findings":[{"issue":"bad","evidence":"trace","deduction":0.2}]}',
        '{"score":0.5,"reason":"partial","findings":[]}',
    ],
)
def test_judge_ambiguous_incomplete_or_contradictory_assessments_rejected(text):
    with pytest.raises(ValueError):
        verifier.parse_verdict(text)


def test_deterministic_scores_give_partial_credit_without_binary_gate():
    result = verifier.assess(events()[2:])
    assert result["task_completion"]["score"] == 1
    assert result["protocol_compliance"]["score"] == 0.75
    assert result["score"] == 0.875
    assert result["passed"] is False


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


def test_outcome_and_protocol_are_independent():
    result = verifier.assess(events()[2:])
    assert result["task_completion"]["passed"] is True
    assert result["protocol_compliance"]["passed"] is False
    assert result["passed"] is False


def test_reports_all_failures_instead_of_first_only():
    result = verifier.assess(events()[2:-2])
    assert {f["check"] for f in result["failures"]} == {
        "connection_observed",
        "verified_post_create_vm",
    }


def test_unrequested_scope_override_fails_even_with_correct_read():
    rows = events()
    rows[4]["message"]["content"][0]["input"]["project_id"] = "another-project"
    result = verifier.assess(rows)
    assert result["task_completion"]["passed"] is False
    assert result["protocol_compliance"]["passed"] is True
    assert {f["check"] for f in result["failures"]} == {"server_defaults_preserved"}


def test_wrong_vm_name_is_not_the_requested_outcome():
    rows = events()
    rows[-1]["message"]["content"][0]["content"][0]["text"] = json.dumps(
        {
            "items": [
                {
                    "id": verifier.VM_ID,
                    "name": "different-vm",
                    "state": "COMPUTE_INSTANCE_STATE_STARTING",
                }
            ]
        }
    )
    assert verifier.assess(rows)["observed_vm"] is None


def test_empty_optional_fields_preserve_server_defaults():
    for key, value in [
        ("project_id", ""),
        ("disk_image_id", None),
        ("network_attachments", []),
        ("boot_disk", {}),
    ]:
        rows = events()
        rows[4]["message"]["content"][0]["input"][key] = value
        assert verifier.assess(rows)["passed"]


def test_missing_vm_state_fails_verification():
    rows = events()
    rows[-1]["message"]["content"][0]["content"][0]["text"] = json.dumps(
        {"items": [{"id": verifier.VM_ID, "name": "uncertain-vm-01"}]}
    )
    assert not verifier.assess(rows)["task_completion"]["passed"]


@pytest.mark.parametrize("native_format", ["claude-code", "codex"])
def test_full_trace_judge_receives_exact_context_and_trace_and_keeps_partial_credit(
    tmp_path, monkeypatch, native_format
):
    import io

    rows = events()[2:] + [
        {
            "type": "result",
            "is_error": False,
            "result": "Observed the VM; some scope remains unknown.",
        }
    ]
    if native_format == "codex":
        rows = codex_events()
    trace_text = "native preamble retained\n" + "\n".join(json.dumps(r) for r in rows)
    trace = tmp_path / ("codex.txt" if native_format == "codex" else "claude-code.txt")
    trace.write_text(trace_text)
    context = {
        "task_request": "Create a VM and verify current status.",
        "shared_environment_context": "Perform necessary read-only checks.",
    }
    (tmp_path / "judge-context.json").write_text(json.dumps(context))
    monkeypatch.setattr(verifier, "STREAM", tmp_path / "claude-code.txt")
    monkeypatch.setattr(verifier, "__file__", str(tmp_path / "test_outputs.py"))
    real_path = Path
    monkeypatch.setattr(
        verifier,
        "Path",
        lambda value: (
            tmp_path / real_path(value).name
            if str(value).startswith("/logs/verifier/")
            else real_path(value)
        ),
    )
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-only")
    captured = {}
    verdict = {
        "score": 0.65,
        "reason": "Partial completion; sound uncertainty handling",
        "findings": [
            {
                "issue": "Incomplete observation",
                "evidence": "A material scope claim remains unverified in the trace",
                "deduction": 0.35,
            }
        ],
    }

    def respond(request, timeout):
        captured.update(json.loads(request.data))
        assert timeout == 90
        return io.StringIO(
            json.dumps({"choices": [{"message": {"content": json.dumps(verdict)}}]})
        )

    monkeypatch.setattr(verifier.urllib.request, "urlopen", respond)
    verifier.test_full_trace_judgment()  # A valid low score is not an infrastructure exception.
    payload = json.loads(captured["messages"][1]["content"])
    assert payload == {
        "task_context": context,
        "full_native_trace": trace_text,
        "final_result": rows[-2] if native_format == "codex" else rows[-1],
        "native_trace_format": native_format,
    }
    assert captured["messages"][0]["content"] == verifier.JUDGMENT_RUBRIC
    assert json.loads((tmp_path / "llm-judge-input.json").read_text()) == captured
    assert "Authorization" not in (tmp_path / "llm-judge-input.json").read_text()
    saved = json.loads((tmp_path / "answer-judge.json").read_text())
    assert saved["score"] == 0.65 and saved["passed"] is False


@pytest.mark.parametrize(
    "score,findings",
    [
        (0.95, [{"issue": "Gap", "evidence": "trace", "deduction": 0.7}]),
        (
            0.0,
            [
                {"issue": "Gap", "evidence": "trace", "deduction": 0.6},
                {"issue": "Other", "evidence": "result", "deduction": 0.6},
            ],
        ),
        (0.5, [{"issue": "Gap", "evidence": "trace", "deduction": True}]),
        (0.5, [{"issue": "Gap", "evidence": "trace", "deduction": float("nan")}]),
        (0.5, [{"issue": "Gap", "evidence": "", "deduction": 0.5}]),
        (0.5, [{"issue": "Gap", "evidence": "trace", "deduction": 0}]),
    ],
)
def test_judge_deductions_require_evidence_and_match_numeric_score(score, findings):
    with pytest.raises(ValueError):
        verifier.parse_verdict(
            json.dumps(
                {"score": score, "reason": "Reviewed full trace", "findings": findings}
            )
        )


def codex_events():
    """Wire shape from openai/codex exec_events.rs, not Claude-shaped logs."""
    calls, results = verifier.observations(events())
    rows = [
        {"type": "thread.started", "thread_id": "thread-fixture"},
        {"type": "turn.started"},
    ]
    for call in calls:
        result = results[call["id"]]
        item = {
            "id": call["id"],
            "type": "mcp_tool_call",
            "server": "osac",
            "tool": call["name"].rsplit("__", 1)[-1],
            "arguments": call["input"],
            "status": "in_progress",
            "result": None,
            "error": None,
        }
        rows.append({"type": "item.started", "item": dict(item)})
        item.update(
            status="failed" if result["is_error"] else "completed",
            result=None
            if result["is_error"]
            else {"content": result["content"], "structured_content": None},
            error={"message": "DeadlineExceeded"} if result["is_error"] else None,
        )
        rows.append({"type": "item.completed", "item": item})
    rows.extend(
        [
            {
                "type": "item.completed",
                "item": {
                    "id": "answer",
                    "type": "agent_message",
                    "text": "Observed the VM in STARTING; readiness is unverified.",
                },
            },
            {
                "type": "turn.completed",
                "usage": {
                    "input_tokens": 50,
                    "cached_input_tokens": 0,
                    "output_tokens": 20,
                },
            },
        ]
    )
    return rows


def test_codex_native_observations_preserve_errors_and_dispatches():
    rows = codex_events()
    assert verifier.assess(rows)["passed"]
    calls, results = verifier.observations(rows)
    assert len(calls) == 4
    assert results["2"]["is_error"] is True
    assert verifier.final_result(rows, "codex") == rows[-2]


@pytest.mark.parametrize(
    "mutation",
    ["missing_result", "duplicate_terminal", "changed_args", "nonterminal_result"],
)
def test_codex_invalid_tool_events_rejected(mutation):
    rows = codex_events()
    if mutation == "missing_result":
        rows[3]["item"]["result"] = None
    elif mutation == "duplicate_terminal":
        rows.insert(4, rows[3])
    elif mutation == "changed_args":
        rows[3]["item"]["arguments"] = {"fabricated": True}
    else:
        rows[3]["item"]["status"] = "in_progress"
    with pytest.raises(AssertionError):
        verifier.observations(rows)


def test_codex_missing_terminal_read_cannot_pass():
    rows = codex_events()
    del rows[9]
    evidence = verifier.assess(rows)
    assert not evidence["task_completion"]["checks"]["verified_post_create_vm"]
    assert evidence["calls"][-1]["outcome"] == "missing"


def test_codex_alternative_interface_detected():
    rows = codex_events()
    rows.insert(
        2,
        {
            "type": "item.completed",
            "item": {
                "id": "shell",
                "type": "command_execution",
                "command": "curl https://osac.invalid",
                "status": "completed",
                "exit_code": 0,
                "aggregated_output": "",
            },
        },
    )
    assert not verifier.assess(rows)["protocol_compliance"]["checks"][
        "mcp_interface_only"
    ]


@pytest.mark.parametrize(
    "mutation", ["turn_failed", "error", "missing_completion", "empty_answer"]
)
def test_codex_incomplete_or_failed_turn_rejected(mutation):
    rows = codex_events()
    if mutation in {"turn_failed", "error"}:
        rows.insert(
            -1,
            {
                "type": mutation.replace("_", "."),
                "error": {"message": "provider failed"},
            },
        )
    elif mutation == "missing_completion":
        rows.pop()
    else:
        rows[-2]["item"]["text"] = " "
    with pytest.raises(AssertionError):
        verifier.final_result(rows, "codex")


def test_trace_selection_uses_real_codex_filename_and_rejects_ambiguity(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(verifier, "STREAM", tmp_path / "claude-code.txt")
    codex = tmp_path / "codex.txt"
    codex.write_text("\n".join(json.dumps(r) for r in codex_events()))
    assert verifier.trace_format() == "codex"
    assert verifier.stream() == codex_events()
    (tmp_path / "claude-code.txt").write_text("{}")
    with pytest.raises(AssertionError, match="unambiguous"):
        verifier.trace_path()
