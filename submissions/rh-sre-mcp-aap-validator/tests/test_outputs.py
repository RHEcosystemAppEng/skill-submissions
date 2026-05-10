"""
Tests for rh-sre__mcp-aap-validator evaluation.

6 pytest (1 padding + 5 skill-specific) targeting AAP MCP validation
knowledge: two-axis validation, page_size parameter, gateway vs UI
URL distinction, env var awareness, and structured outcome table.
"""
import os
import pytest

REPORT = "/solution/report.md"


def read_report():
    if not os.path.exists(REPORT):
        pytest.fail(f"Required file not found: {REPORT}")
    with open(REPORT) as f:
        return f.read()


def test_mentions_aap_mcp():
    """Padding: report exists and mentions AAP/MCP."""
    content = read_report().lower()
    assert len(content) > 150 and ("aap" in content or "mcp" in content)


def test_two_axis_validation():
    """Skill teaches validating BOTH job_templates_list AND
    inventories_list as separate connectivity probes. Without skill,
    agents make a single generic connectivity check."""
    c = read_report()
    has_job = "job_templates_list" in c or "job-management" in c
    has_inv = "inventories_list" in c or "inventory-management" in c
    assert has_job and has_inv, (
        "must validate BOTH job template AND inventory MCP capabilities"
    )


def test_page_size_parameter():
    """Skill teaches using page_size: 10 for lightweight connectivity
    probes. Without skill, agents call with no params or wrong params
    (e.g. per_page from Lightspeed)."""
    c = read_report()
    assert "page_size" in c, (
        "must reference page_size parameter for AAP tool calls"
    )


def test_gateway_vs_ui_url():
    """Skill teaches that 404 usually means AAP_MCP_SERVER points to
    the AAP Web UI instead of the MCP gateway endpoint. Without skill,
    agents diagnose 404 as 'server not found'."""
    c = read_report().lower()
    has_404 = "404" in c
    has_gateway = any(t in c for t in [
        "gateway", "mcp gateway", "mcp endpoint",
        "aap_mcp_server", "aap ui", "web ui",
    ])
    assert has_404 and has_gateway, (
        "must explain 404 as gateway vs UI URL misconfiguration"
    )


def test_env_var_awareness():
    """Skill teaches specific env vars: AAP_MCP_SERVER and
    AAP_API_TOKEN. Without skill, agents use generic 'check your
    API key' advice."""
    c = read_report()
    has_server = "AAP_MCP_SERVER" in c
    has_token = "AAP_API_TOKEN" in c
    assert has_server or has_token, (
        "must reference AAP_MCP_SERVER or AAP_API_TOKEN env vars"
    )


def test_structured_outcome_table():
    """Skill teaches ending with a per-server outcome table using
    PASSED/FAILED/PARTIAL. Without skill, agents produce unstructured
    prose."""
    c = read_report()
    has_table = "|" in c
    has_outcome = any(t in c.upper() for t in ["PASSED", "FAILED", "PARTIAL"])
    assert has_table and has_outcome, (
        "must include a structured outcome table with PASSED/FAILED"
    )
