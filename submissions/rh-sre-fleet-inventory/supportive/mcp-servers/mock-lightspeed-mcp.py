#!/usr/bin/env python3
"""
Mock Lightspeed MCP Server

Simulates the Red Hat Lightspeed MCP server for SRE benchmark tasks.
Implements the MCP protocol via FastMCP with response formats matching
the real Lightspeed API so that skill-provided tools (parser scripts,
flow files) work correctly.

Fleet: 63 systems across production/staging/development/QA/legacy.
CVEs: 5 top-level CVEs + ~200 per-system CVEs (for pagination testing).

Key API behaviors reproduced:
  - get_system_cves: pagination via limit/offset, ~200 CVEs per system,
    remediatable CVEs scattered across pages (first page often returns 0)
  - Response format: {result: {data: [{id, type, attributes}]}, meta: {count}}
  - find_host_by_name: hostname -> system_uuid resolution
  - list_hosts: paginated host listing with per_page parameter
  - get_cve: include_details parameter for full metadata
"""

import hashlib
import os
import random
from datetime import datetime, timedelta
from typing import Optional

from fastmcp import FastMCP

random.seed(42)

REFERENCE_TIME = datetime(2026, 2, 15, 12, 0, 0)


def _ts(delta: timedelta) -> str:
    return (REFERENCE_TIME - delta).isoformat() + "Z"


def _uuid_from_id(system_id: str) -> str:
    """Deterministic UUID from system ID."""
    h = hashlib.md5(system_id.encode()).hexdigest()
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


# ---------------------------------------------------------------------------
# Mock fleet data (same 63 systems as before, now with UUIDs)
# ---------------------------------------------------------------------------

def generate_mock_systems() -> list[dict]:
    systems: list[dict] = []
    sid = 1

    def _add(name_prefix, env_prefix, env_tag, tier_tag, count, rhel_fn,
             stale_idx=None, extra_tags_fn=None, satellite=False):
        nonlocal sid
        for i in range(1, count + 1):
            system_id = f"sys-{sid:03d}-{name_prefix}-{env_prefix}-{i:02d}"
            display = f"{name_prefix}-server-{i:02d}.{env_prefix}.example.com"
            if name_prefix in ("cache", "monitor") and count == 1:
                display = f"{name_prefix}-server-01.{env_prefix}.example.com"
                system_id = f"sys-{sid:03d}-{name_prefix}-{env_prefix}-01"
            stale = stale_idx is not None and i == stale_idx
            tags = [env_tag, tier_tag] if tier_tag else [env_tag]
            if extra_tags_fn:
                tags.extend(extra_tags_fn(i))
            systems.append({
                "id": system_id,
                "system_uuid": _uuid_from_id(system_id),
                "display_name": display,
                "fqdn": display,
                "rhel_version": rhel_fn(i),
                "last_seen": _ts(timedelta(days=9 + i) if stale else timedelta(hours=random.randint(1, 22))),
                "tags": tags,
                "stale": stale,
                "satellite_managed": satellite,
            })
            sid += 1

    # Production
    _add("web", "prod", "production", "web-tier", 8,
         lambda i: "9.3" if i <= 5 else ("9.2" if i <= 7 else "8.9"),
         stale_idx=7,
         extra_tags_fn=lambda i: (["customer-facing", "pci-compliant", "high-availability"] if i <= 4 else []) + (["critical"] if i <= 2 else []))
    _add("db", "prod", "production", "database-tier", 6,
         lambda i: "9.3" if i <= 4 else "9.2",
         stale_idx=5,
         extra_tags_fn=lambda i: (["critical"] + (["pci-compliant", "soc2-compliant", "high-availability"] if i <= 4 else []) + (["customer-data"] if i <= 2 else [])))
    _add("app", "prod", "production", "app-tier", 10,
         lambda i: "8.9" if i <= 6 else ("9.2" if i <= 8 else "9.3"),
         stale_idx=9,
         extra_tags_fn=lambda i: (["customer-facing", "pci-compliant", "soc2-compliant"] if i <= 3 else (["hipaa-compliant", "soc2-compliant"] if i <= 6 else [])) + (["high-availability"] if i <= 5 else []))
    _add("lb", "prod", "production", "loadbalancer", 3,
         lambda _: "8.8",
         extra_tags_fn=lambda i: ["critical", "high-availability"] + (["customer-facing"] if i <= 2 else []))
    _add("monitor", "prod", "production", "monitoring", 2, lambda _: "9.3")
    # Cache (stale)
    systems.append({
        "id": f"sys-{sid:03d}-cache-prod-01",
        "system_uuid": _uuid_from_id(f"sys-{sid:03d}-cache-prod-01"),
        "display_name": "cache-server-01.prod.example.com",
        "fqdn": "cache-server-01.prod.example.com",
        "rhel_version": "8.9", "last_seen": _ts(timedelta(days=11)),
        "tags": ["production", "cache-tier"], "stale": True, "satellite_managed": False,
    })
    sid += 1

    # Staging
    _add("web", "stg", "staging", "web-tier", 4,
         lambda i: "9.3" if i <= 2 else "9.2", stale_idx=3)
    _add("db", "stg", "staging", "database-tier", 3,
         lambda i: "9.3" if i <= 2 else "9.2")
    _add("app", "stg", "staging", "app-tier", 5,
         lambda i: "8.9" if i <= 3 else "9.2")
    _add("lb", "stg", "staging", "loadbalancer", 2, lambda _: "8.8")
    systems.append({
        "id": f"sys-{sid:03d}-mon-stg-01",
        "system_uuid": _uuid_from_id(f"sys-{sid:03d}-mon-stg-01"),
        "display_name": "monitor-server-01.staging.example.com",
        "fqdn": "monitor-server-01.staging.example.com",
        "rhel_version": "9.3", "last_seen": _ts(timedelta(hours=8)),
        "tags": ["staging", "monitoring"], "stale": False, "satellite_managed": False,
    })
    sid += 1

    # Development
    _add("web", "dev", "development", "web-tier", 3,
         lambda i: "9.2" if i == 1 else "8.9", stale_idx=2)
    _add("db", "dev", "development", "database-tier", 2,
         lambda i: "9.3" if i == 1 else "9.2")
    _add("app", "dev", "development", "app-tier", 4,
         lambda i: "8.9" if i <= 2 else "9.2")
    systems.append({
        "id": f"sys-{sid:03d}-mon-dev-01",
        "system_uuid": _uuid_from_id(f"sys-{sid:03d}-mon-dev-01"),
        "display_name": "monitor-server-01.dev.example.com",
        "fqdn": "monitor-server-01.dev.example.com",
        "rhel_version": "9.2", "last_seen": _ts(timedelta(hours=10)),
        "tags": ["development", "monitoring"], "stale": False, "satellite_managed": False,
    })
    sid += 1

    # QA
    _add("web", "qa", "qa", "web-tier", 2,
         lambda _: "9.3", stale_idx=2)
    systems.append({
        "id": f"sys-{sid:03d}-db-qa-01",
        "system_uuid": _uuid_from_id(f"sys-{sid:03d}-db-qa-01"),
        "display_name": "db-server-01.qa.example.com",
        "fqdn": "db-server-01.qa.example.com",
        "rhel_version": "9.2", "last_seen": _ts(timedelta(hours=12)),
        "tags": ["qa", "database-tier"], "stale": False, "satellite_managed": False,
    })
    sid += 1
    _add("app", "qa", "qa", "app-tier", 2,
         lambda _: "9.2")

    # Legacy
    for name, fqdn, rhel, tags, stale_days in [
        ("legacy-payment-gw", "legacy-payment-gw.example.com", "8.7",
         ["legacy-system", "payment-gateway", "critical"], 0.125),
        ("reports-legacy", "reports-legacy.example.com", "8.6",
         ["legacy-system", "reporting", "financial-data"], 6),
        ("archive-01", "archive-01.legacy.example.com", "8.5",
         ["legacy-system", "archive", "read-only"], 30),
    ]:
        systems.append({
            "id": f"sys-{sid:03d}-{name}",
            "system_uuid": _uuid_from_id(f"sys-{sid:03d}-{name}"),
            "display_name": fqdn, "fqdn": fqdn,
            "rhel_version": rhel,
            "last_seen": _ts(timedelta(days=stale_days)),
            "tags": tags, "stale": stale_days > 7,
            "satellite_managed": True,
        })
        sid += 1

    return systems


MOCK_SYSTEMS = generate_mock_systems()
SYSTEM_BY_UUID = {s["system_uuid"]: s for s in MOCK_SYSTEMS}
SYSTEM_BY_NAME = {}
for s in MOCK_SYSTEMS:
    SYSTEM_BY_NAME[s["display_name"]] = s
    SYSTEM_BY_NAME[s["fqdn"]] = s
    short = s["display_name"].split(".")[0]
    SYSTEM_BY_NAME[short] = s

# ---------------------------------------------------------------------------
# Mock CVE data — top-level CVEs (for get_cve, get_cve_systems)
# ---------------------------------------------------------------------------

MOCK_CVE_DATA = {
    "CVE-2024-12345": {
        "severity": "Critical", "cvss3_score": "9.8",
        "description": "Remote code execution vulnerability in HTTP request processing",
        "advisory_available": True, "remediation": 2,
        "advisories_list": ["RHSA-2024:0123"],
        "synopsis": "Critical: httpd security update",
        "public_date": "2024-01-15",
        "affected_systems": [
            {"system_id": "sys-001-web-prod-01", "display_name": "web-server-01.prod.example.com", "status": "Vulnerable", "remediation_available": True},
            {"system_id": "sys-002-web-prod-02", "display_name": "web-server-02.prod.example.com", "status": "Vulnerable", "remediation_available": True},
            {"system_id": "sys-003-web-prod-03", "display_name": "web-server-03.prod.example.com", "status": "Vulnerable", "remediation_available": True},
            {"system_id": "sys-004-web-prod-04", "display_name": "web-server-04.prod.example.com", "status": "Patched", "remediation_available": True},
            {"system_id": "sys-031-web-stg-01", "display_name": "web-server-01.staging.example.com", "status": "Vulnerable", "remediation_available": True},
            {"system_id": "sys-032-web-stg-02", "display_name": "web-server-02.staging.example.com", "status": "Patched", "remediation_available": True},
        ],
    },
    "CVE-2024-54321": {
        "severity": "Important", "cvss3_score": "7.5",
        "description": "SQL injection vulnerability in database query parser",
        "advisory_available": True, "remediation": 2,
        "advisories_list": ["RHSA-2024:0456"],
        "synopsis": "Important: postgresql security update",
        "public_date": "2024-02-20",
        "affected_systems": [
            {"system_id": "sys-009-db-prod-01", "display_name": "db-server-01.prod.example.com", "status": "Vulnerable", "remediation_available": True},
            {"system_id": "sys-010-db-prod-02", "display_name": "db-server-02.prod.example.com", "status": "Vulnerable", "remediation_available": True},
            {"system_id": "sys-011-db-prod-03", "display_name": "db-server-03.prod.example.com", "status": "Patched", "remediation_available": True},
            {"system_id": "sys-012-db-prod-04", "display_name": "db-server-04.prod.example.com", "status": "Patched", "remediation_available": True},
            {"system_id": "sys-035-db-stg-01", "display_name": "db-server-01.staging.example.com", "status": "Vulnerable", "remediation_available": True},
        ],
    },
    "CVE-2024-11111": {
        "severity": "Moderate", "cvss3_score": "5.3",
        "description": "Information disclosure in application logging",
        "advisory_available": True, "remediation": 2,
        "advisories_list": ["RHSA-2024:0789"],
        "synopsis": "Moderate: app-framework security update",
        "public_date": "2024-03-10",
        "affected_systems": [
            {"system_id": f"sys-{15+i:03d}-app-prod-{i:02d}", "display_name": f"app-server-{i:02d}.prod.example.com",
             "status": "Vulnerable", "remediation_available": True}
            for i in range(1, 7)
        ] + [
            {"system_id": "sys-022-app-prod-07", "display_name": "app-server-07.prod.example.com",
             "status": "Not Affected", "remediation_available": True},
            {"system_id": "sys-023-app-prod-08", "display_name": "app-server-08.prod.example.com",
             "status": "Not Affected", "remediation_available": True},
        ],
    },
    "CVE-2024-98765": {
        "severity": "Important", "cvss3_score": "8.1",
        "description": "Denial of service vulnerability in load balancer traffic handling",
        "advisory_available": True, "remediation": 2,
        "advisories_list": ["RHSA-2024:1012"],
        "synopsis": "Important: haproxy security update",
        "public_date": "2024-04-05",
        "affected_systems": [
            {"system_id": "sys-025-lb-prod-01", "display_name": "lb-server-01.prod.example.com", "status": "Vulnerable", "remediation_available": True},
            {"system_id": "sys-026-lb-prod-02", "display_name": "lb-server-02.prod.example.com", "status": "Vulnerable", "remediation_available": True},
            {"system_id": "sys-027-lb-prod-03", "display_name": "lb-server-03.prod.example.com", "status": "Vulnerable", "remediation_available": True},
            {"system_id": "sys-045-lb-stg-01", "display_name": "lb-server-01.staging.example.com", "status": "Patched", "remediation_available": True},
        ],
    },
    "CVE-2024-22222": {
        "severity": "Low", "cvss3_score": "3.1",
        "description": "Minor information disclosure in monitoring agent error messages",
        "advisory_available": False, "remediation": 0,
        "advisories_list": [],
        "synopsis": "Low: monitoring-agent information disclosure",
        "public_date": "2024-05-01",
        "affected_systems": [
            {"system_id": "sys-028-mon-prod-01", "display_name": "monitor-server-01.prod.example.com", "status": "Vulnerable", "remediation_available": False},
            {"system_id": "sys-029-mon-prod-02", "display_name": "monitor-server-02.prod.example.com", "status": "Vulnerable", "remediation_available": False},
        ],
    },
}


# ---------------------------------------------------------------------------
# Per-system CVE generator (for get_system_cves pagination testing)
# Produces ~200 CVEs per system. Remediatable ones are SCATTERED across pages
# so that first page (offset=0, limit=100) returns 0 remediatable CVEs —
# matching real-world Lightspeed behavior.
# ---------------------------------------------------------------------------

_SEVERITIES = ["Critical", "Important", "Moderate", "Low"]
_SEVERITY_WEIGHTS = [0.05, 0.15, 0.40, 0.40]


def _generate_system_cves(system_uuid: str) -> list[dict]:
    """Generate ~200 deterministic CVEs for a system. Remediatable CVEs
    appear mostly after index 100 to simulate real pagination behavior."""
    rng = random.Random(system_uuid)
    total = rng.randint(180, 220)
    cves = []
    for idx in range(total):
        year = rng.choice([2023, 2024, 2025])
        num = rng.randint(10000, 99999)
        cve_id = f"CVE-{year}-{num}"

        sev = rng.choices(_SEVERITIES, weights=_SEVERITY_WEIGHTS, k=1)[0]
        cvss = {"Critical": rng.uniform(9.0, 10.0), "Important": rng.uniform(7.0, 8.9),
                "Moderate": rng.uniform(4.0, 6.9), "Low": rng.uniform(0.1, 3.9)}[sev]

        # Remediatable CVEs: ~15% overall, but concentrated AFTER index 100
        if idx < 100:
            advisory = rng.random() < 0.02  # ~2% in first 100
        else:
            advisory = rng.random() < 0.28  # ~28% in later pages

        cves.append({
            "id": cve_id,
            "type": "cve",
            "url": f"https://console.redhat.com/insights/vulnerability/cves/{cve_id}",
            "attributes": {
                "advisory_available": advisory,
                "impact": sev,
                "cvss3_score": f"{cvss:.1f}",
                "cvss2_score": None,
                "description": f"Mock vulnerability {cve_id}",
                "synopsis": f"{sev}: mock security update for {cve_id}",
                "public_date": f"{year}-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}",
                "business_risk": rng.choice(["High", "Medium", "Low", "Not Defined"]),
                "rules": [],
            },
        })
    return cves


_SYSTEM_CVE_CACHE: dict[str, list[dict]] = {}


def _get_cached_system_cves(system_uuid: str) -> list[dict]:
    if system_uuid not in _SYSTEM_CVE_CACHE:
        _SYSTEM_CVE_CACHE[system_uuid] = _generate_system_cves(system_uuid)
    return _SYSTEM_CVE_CACHE[system_uuid]


# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------

mcp = FastMCP("lightspeed-mcp")


@mcp.tool
def get_host_details(
    system_id: Optional[str] = None,
    hostname_pattern: Optional[str] = None,
    tags: Optional[list[str]] = None,
    rhel_version_prefix: Optional[str] = None,
) -> dict:
    """Retrieve registered system inventory from Red Hat Lightspeed.

    Returns all systems when called with no arguments. Supports filtering
    by system ID, hostname pattern, tags, and RHEL version prefix.
    """
    filtered = list(MOCK_SYSTEMS)
    if system_id:
        filtered = [s for s in filtered if s["id"] == system_id or s["system_uuid"] == system_id]
    if hostname_pattern:
        pattern = hostname_pattern.replace("*", "")
        filtered = [s for s in filtered if pattern in s["fqdn"]]
    if tags:
        filtered = [s for s in filtered if any(t in s.get("tags", []) for t in tags)]
    if rhel_version_prefix:
        filtered = [s for s in filtered if s["rhel_version"].startswith(rhel_version_prefix)]
    return {"systems": filtered, "total": len(MOCK_SYSTEMS), "count": len(filtered)}


@mcp.tool
def find_host_by_name(display_name: str) -> dict:
    """Resolve a hostname or display name to a system UUID.

    Args:
        display_name: Hostname, FQDN, or display name to look up.
    """
    if display_name in SYSTEM_BY_NAME:
        s = SYSTEM_BY_NAME[display_name]
        return {"results": [s], "count": 1}
    # Partial match
    matches = [s for s in MOCK_SYSTEMS if display_name.lower() in s["fqdn"].lower()]
    if matches:
        return {"results": matches, "count": len(matches)}
    return {"results": [], "count": 0}


@mcp.tool
def list_hosts(
    per_page: int = 10,
    page: int = 1,
    display_name: Optional[str] = None,
) -> dict:
    """List hosts with pagination. Use per_page (NOT page_size).

    Args:
        per_page: Number of results per page (integer, NOT page_size).
        page: Page number (1-based).
        display_name: Filter by display name (empty string for no filter).
    """
    filtered = MOCK_SYSTEMS
    if display_name:
        filtered = [s for s in filtered if display_name.lower() in s["display_name"].lower()]
    start = (page - 1) * per_page
    end = start + per_page
    page_results = filtered[start:end]
    return {
        "results": page_results,
        "count": len(page_results),
        "total": len(filtered),
        "per_page": per_page,
        "page": page,
    }


@mcp.tool
def get_system_cves(
    system_uuid: str,
    limit: int = 10,
    offset: int = 0,
    sort: Optional[str] = None,
) -> dict:
    """List CVEs affecting a specific system. Supports pagination.

    IMPORTANT: Use system_uuid (NOT system_id or hostname).
    Does NOT support impact or advisory_available filters — filter client-side.

    Args:
        system_uuid: System UUID (required). Use find_host_by_name to resolve.
        limit: Records per page (default 10, max 100).
        offset: Pagination offset.
        sort: Sort field with optional - prefix for descending.
    """
    if system_uuid not in SYSTEM_BY_UUID:
        return {"error": f"System {system_uuid} not found", "result": {"data": []}, "meta": {"count": 0}}

    all_cves = _get_cached_system_cves(system_uuid)
    page = all_cves[offset:offset + limit]

    return {
        "result": {"data": page},
        "meta": {"count": len(all_cves)},
    }


@mcp.tool
def get_cve_systems(cve_id: str) -> dict:
    """Find systems affected by a specific CVE.

    Args:
        cve_id: CVE identifier in CVE-YYYY-NNNNN format.
    """
    if cve_id in MOCK_CVE_DATA:
        cve = MOCK_CVE_DATA[cve_id]
        return {
            "cve_id": cve_id,
            "affected_systems": cve["affected_systems"],
            "total_affected": len(cve["affected_systems"]),
            "total_remediated": sum(1 for s in cve["affected_systems"] if s["status"] == "Patched"),
            "total_vulnerable": sum(1 for s in cve["affected_systems"] if s["status"] == "Vulnerable"),
        }
    return {"cve_id": cve_id, "affected_systems": [], "total_affected": 0, "total_remediated": 0}


@mcp.tool
def get_cves(
    impact: Optional[str] = None,
    sort: Optional[str] = None,
    advisory_available: Optional[str] = None,
) -> dict:
    """List all known CVEs affecting the fleet.

    Args:
        impact: Comma-separated impact IDs (7=Critical, 6=High/Important, 5=Moderate, 4=Low).
        sort: Sort field (e.g. '-cvss_score').
        advisory_available: Filter: 'true' = only with remediation.
    """
    impact_map = {"7": "Critical", "6": "Important", "5": "Moderate", "4": "Low"}
    summaries = []
    for cve_id, cve in MOCK_CVE_DATA.items():
        if impact:
            allowed = [impact_map.get(x.strip(), "") for x in impact.split(",")]
            if cve["severity"] not in allowed:
                continue
        if advisory_available == "true" and not cve["advisory_available"]:
            continue

        summaries.append({
            "id": cve_id,
            "type": "cve",
            "url": f"https://console.redhat.com/insights/vulnerability/cves/{cve_id}",
            "attributes": {
                "advisory_available": cve["advisory_available"],
                "impact": cve["severity"],
                "cvss3_score": cve["cvss3_score"],
                "synopsis": cve["synopsis"],
                "public_date": cve["public_date"],
            },
        })

    return {"result": {"data": summaries}, "meta": {"count": len(summaries)}}


@mcp.tool
def get_cve(cve_id: str, include_details: bool = False) -> dict:
    """Get detailed information about a specific CVE.

    Args:
        cve_id: CVE identifier in CVE-YYYY-NNNNN format.
        include_details: If true, include full metadata (CVSS vector, packages).
    """
    if cve_id not in MOCK_CVE_DATA:
        return {"error": f"CVE {cve_id} not found"}

    cve = MOCK_CVE_DATA[cve_id]
    result = {
        "id": cve_id,
        "type": "cve",
        "attributes": {
            "advisory_available": cve["advisory_available"],
            "remediation": cve["remediation"],
            "advisories_list": cve["advisories_list"],
            "impact": cve["severity"],
            "cvss3_score": cve["cvss3_score"],
            "description": cve["description"],
            "synopsis": cve["synopsis"],
            "public_date": cve["public_date"],
            "rules": [],
        },
    }
    if include_details:
        result["attributes"]["cvss3_scoring_vector"] = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
        result["attributes"]["affected_packages"] = ["httpd-2.4.37-1.el8", "openssl-1.1.1k-7.el8"]
        result["attributes"]["references"] = [
            f"https://access.redhat.com/security/cve/{cve_id}",
            f"https://nvd.nist.gov/vuln/detail/{cve_id}",
        ]
    return result


@mcp.tool
def create_vulnerability_playbook(
    cve_id: str,
    system_ids: Optional[list[str]] = None,
) -> dict:
    """Generate an Ansible remediation playbook for a CVE.

    Args:
        cve_id: CVE identifier to remediate.
        system_ids: Specific system IDs to target. Omit for all vulnerable.
    """
    if cve_id not in MOCK_CVE_DATA:
        return {"error": f"CVE {cve_id} not found"}
    cve = MOCK_CVE_DATA[cve_id]
    if not cve["advisory_available"]:
        return {"error": "No automated remediation available", "cve_id": cve_id}
    targets = system_ids or [
        s["system_id"] for s in cve["affected_systems"] if s["status"] == "Vulnerable"
    ]
    return {
        "cve_id": cve_id, "playbook_id": f"playbook-{cve_id.lower()}-mock",
        "target_systems": targets, "target_count": len(targets), "status": "generated",
        "playbook_content": (
            f"---\n- hosts: targeted_systems\n  become: true\n  tasks:\n"
            f"    - name: Apply patch for {cve_id}\n"
            f"      dnf:\n        name: '*'\n        state: latest\n        security: true\n"
        ),
    }


if __name__ == "__main__":
    mcp.run()
