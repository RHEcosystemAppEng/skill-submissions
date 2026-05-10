"""
Tests for rh-sre__mcp-lightspeed-validator evaluation.

6 pytest (1 padding + 5 skill-specific) targeting Lightspeed MCP
validation knowledge: no-args connectivity probe, limit_ bug,
credential env vars, secret handling, and structured outcome table.
"""
import os
import pytest

REPORT = "/solution/report.md"


def read_report():
    if not os.path.exists(REPORT):
        pytest.fail(f"Required file not found: {REPORT}")
    with open(REPORT) as f:
        return f.read()


def test_mentions_lightspeed_mcp():
    """Padding: report exists and mentions Lightspeed/MCP."""
    content = read_report().lower()
    assert len(content) > 150 and ("lightspeed" in content or "mcp" in content)


def test_no_args_connectivity_probe():
    """Skill teaches calling get_cves with NO arguments as the correct
    connectivity test. Without skill, agents pass limit or other params
    that trigger the limit_ serialization bug."""
    c = read_report().lower()
    has_no_args = any(t in c for t in [
        "no param", "no argument", "without param", "without argument",
        "default", "no-arg", "empty",
    ])
    has_get_cves = "get_cves" in c or "vulnerability" in c
    assert has_no_args and has_get_cves, (
        "must explain calling get_cves with no parameters for connectivity"
    )


def test_limit_underscore_bug():
    """Skill teaches the limit -> limit_ parameter serialization bug
    that causes 'Unexpected keyword argument' errors. Without skill,
    agents retry the same failing call or treat it as opaque."""
    c = read_report()
    has_limit_bug = "limit_" in c
    has_limit_issue = any(t in c.lower() for t in [
        "unexpected keyword", "serializ", "parameter naming",
        "do not pass limit",
    ])
    assert has_limit_bug or has_limit_issue, (
        "must reference the limit_ serialization bug or parameter issue"
    )


def test_lightspeed_credentials():
    """Skill teaches specific env vars: LIGHTSPEED_CLIENT_ID and
    LIGHTSPEED_CLIENT_SECRET. Without skill, agents use generic
    'check API key' advice."""
    c = read_report()
    has_client_id = "LIGHTSPEED_CLIENT_ID" in c or "CLIENT_ID" in c
    has_client_secret = "LIGHTSPEED_CLIENT_SECRET" in c or "CLIENT_SECRET" in c
    assert has_client_id or has_client_secret, (
        "must reference LIGHTSPEED_CLIENT_ID or CLIENT_SECRET env vars"
    )


def test_secret_handling():
    """Skill teaches never echoing credentials -- verify presence
    without printing values. Without skill, agents may paste or
    expose credential values."""
    c = read_report().lower()
    assert any(t in c for t in [
        "never echo", "do not echo", "redact", "sensitive",
        "never print", "never display", "never expose",
        "don't echo", "do not display", "do not expose",
        "credential", "secret",
    ]), "must mention credential safety (never echo/redact secrets)"


def test_structured_outcome_table():
    """Skill teaches ending with a Server | Outcome table using
    PASSED/FAILED. Without skill, agents produce unstructured prose."""
    c = read_report()
    has_table = "|" in c
    has_outcome = any(t in c.upper() for t in ["PASSED", "FAILED"])
    assert has_table and has_outcome, (
        "must include a structured outcome table with PASSED/FAILED"
    )
