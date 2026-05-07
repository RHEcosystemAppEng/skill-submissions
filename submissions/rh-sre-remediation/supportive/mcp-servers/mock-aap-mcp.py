#!/usr/bin/env python3
"""
Mock AAP MCP Server

Simulates the Ansible Automation Platform MCP servers for SRE benchmark tasks.
Combines both aap-mcp-job-management and aap-mcp-inventory-management into a
single FastMCP server. Response formats match the real AAP Controller API so
that skill-provided workflows (remediation SKILL.md) work correctly.

Inventories: 3 environments (production, staging, development) with hosts
drawn from the same fleet as mock-lightspeed-mcp.py.

Job templates: Pre-seeded CVE remediation templates matching mock CVE data.
"""

import hashlib
import time
from datetime import datetime, timedelta
from typing import Optional

from fastmcp import FastMCP

REFERENCE_TIME = datetime(2026, 2, 15, 14, 0, 0)

# ---------------------------------------------------------------------------
# Mock inventories
# ---------------------------------------------------------------------------

MOCK_INVENTORIES = [
    {
        "id": 1,
        "name": "production",
        "description": "Production RHEL fleet",
        "total_hosts": 30,
        "has_active_failures": False,
        "organization": "Red Hat SRE",
    },
    {
        "id": 2,
        "name": "staging",
        "description": "Staging RHEL fleet",
        "total_hosts": 15,
        "has_active_failures": False,
        "organization": "Red Hat SRE",
    },
    {
        "id": 3,
        "name": "development",
        "description": "Development RHEL fleet",
        "total_hosts": 10,
        "has_active_failures": False,
        "organization": "Red Hat SRE",
    },
]

INVENTORY_BY_ID = {inv["id"]: inv for inv in MOCK_INVENTORIES}
INVENTORY_BY_NAME = {inv["name"]: inv for inv in MOCK_INVENTORIES}

# Host data per inventory (subset of the 63-system fleet)
_ENV_HOSTS: dict[int, list[dict]] = {
    1: [  # production
        {"id": i, "name": f"{role}-server-{n:02d}.prod.example.com",
         "enabled": True, "has_active_failures": False,
         "inventory": 1}
        for i, (role, n) in enumerate([
            *[("web", j) for j in range(1, 9)],
            *[("db", j) for j in range(1, 7)],
            *[("app", j) for j in range(1, 11)],
            *[("lb", j) for j in range(1, 4)],
            ("monitor", 1), ("monitor", 2), ("cache", 1),
        ], start=1)
    ],
    2: [  # staging
        {"id": i, "name": f"{role}-server-{n:02d}.staging.example.com",
         "enabled": True, "has_active_failures": False,
         "inventory": 2}
        for i, (role, n) in enumerate([
            *[("web", j) for j in range(1, 5)],
            *[("db", j) for j in range(1, 4)],
            *[("app", j) for j in range(1, 6)],
            *[("lb", j) for j in range(1, 3)],
            ("monitor", 1),
        ], start=100)
    ],
    3: [  # development
        {"id": i, "name": f"{role}-server-{n:02d}.dev.example.com",
         "enabled": True, "has_active_failures": False,
         "inventory": 3}
        for i, (role, n) in enumerate([
            *[("web", j) for j in range(1, 4)],
            *[("db", j) for j in range(1, 3)],
            *[("app", j) for j in range(1, 5)],
            ("monitor", 1),
        ], start=200)
    ],
}

# ---------------------------------------------------------------------------
# Mock job templates (pre-seeded for known CVEs)
# ---------------------------------------------------------------------------

MOCK_JOB_TEMPLATES = [
    {
        "id": 101,
        "name": "CVE-2024-12345 Remediation - httpd security update",
        "description": "Apply RHSA-2024:0123 patch for CVE-2024-12345 (Critical RCE in HTTP request processing)",
        "playbook": "remediate_cve_2024_12345.yml",
        "inventory": 1,
        "status": "successful",
        "cve_id": "CVE-2024-12345",
    },
    {
        "id": 102,
        "name": "CVE-2024-54321 Remediation - postgresql security update",
        "description": "Apply RHSA-2024:0456 patch for CVE-2024-54321 (SQL injection in database query parser)",
        "playbook": "remediate_cve_2024_54321.yml",
        "inventory": 1,
        "status": "successful",
        "cve_id": "CVE-2024-54321",
    },
    {
        "id": 103,
        "name": "CVE-2024-11111 Remediation - app-framework security update",
        "description": "Apply RHSA-2024:0789 patch for CVE-2024-11111 (Information disclosure in app logging)",
        "playbook": "remediate_cve_2024_11111.yml",
        "inventory": 1,
        "status": "successful",
        "cve_id": "CVE-2024-11111",
    },
    {
        "id": 104,
        "name": "CVE-2024-98765 Remediation - haproxy security update",
        "description": "Apply RHSA-2024:1012 patch for CVE-2024-98765 (DoS in load balancer traffic handling)",
        "playbook": "remediate_cve_2024_98765.yml",
        "inventory": 1,
        "status": "successful",
        "cve_id": "CVE-2024-98765",
    },
]

TEMPLATE_BY_ID = {t["id"]: t for t in MOCK_JOB_TEMPLATES}

# ---------------------------------------------------------------------------
# In-memory job store (launched jobs)
# ---------------------------------------------------------------------------

_next_job_id = 1000
_launched_jobs: dict[int, dict] = {}


def _generate_job_log(job: dict) -> str:
    """Generate realistic Ansible job stdout for a remediation run."""
    cve_id = job.get("cve_id", "CVE-UNKNOWN")
    hosts = job.get("target_hosts", ["targeted-host.example.com"])
    host_list = "\n".join(f"  - {h}" for h in hosts[:5])
    extra = f"\n  ... and {len(hosts) - 5} more hosts" if len(hosts) > 5 else ""

    return f"""PLAY [Apply remediation for {cve_id}] *******************************************

TASK [Gathering Facts] *********************************************************
ok: [{hosts[0]}]

TASK [Check current package versions] ******************************************
ok: [{hosts[0]}]

TASK [Apply security patch for {cve_id}] ***************************************
changed: [{hosts[0]}]

TASK [Verify patch applied] ****************************************************
ok: [{hosts[0]}] => {{
    "msg": "Patch for {cve_id} successfully applied. Package updated to latest security version."
}}

TASK [Restart affected services] ***********************************************
changed: [{hosts[0]}]

PLAY RECAP *********************************************************************
Targeted hosts:
{host_list}{extra}

{hosts[0]}              : ok=5    changed=2    unreachable=0    failed=0    skipped=0

Summary: Remediation for {cve_id} completed successfully on {len(hosts)} host(s).
All targeted systems patched and services restarted.
"""


# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------

mcp = FastMCP("aap-mcp")


# ---- Inventory Management ----

@mcp.tool
def list_inventories() -> dict:
    """List all available AAP inventories.

    Returns inventory objects with id, name, description, and host counts.
    """
    return {
        "count": len(MOCK_INVENTORIES),
        "results": MOCK_INVENTORIES,
    }


@mcp.tool
def get_inventory(inventory_id: int) -> dict:
    """Get details of a specific inventory by ID.

    Args:
        inventory_id: The inventory ID to look up.
    """
    if inventory_id not in INVENTORY_BY_ID:
        return {"error": f"Inventory {inventory_id} not found"}
    return INVENTORY_BY_ID[inventory_id]


@mcp.tool
def get_inventory_hosts(
    inventory_id: int,
    page: int = 1,
    page_size: int = 25,
) -> dict:
    """List hosts in a specific inventory with pagination.

    Args:
        inventory_id: The inventory ID.
        page: Page number (1-based).
        page_size: Number of hosts per page.
    """
    if inventory_id not in _ENV_HOSTS:
        return {"error": f"Inventory {inventory_id} not found", "count": 0, "results": []}

    hosts = _ENV_HOSTS[inventory_id]
    start = (page - 1) * page_size
    end = start + page_size
    page_results = hosts[start:end]

    return {
        "count": len(hosts),
        "results": page_results,
        "page": page,
        "page_size": page_size,
    }


@mcp.tool
def add_host_to_inventory(
    inventory_id: int,
    hostname: str,
    enabled: bool = True,
) -> dict:
    """Add a host to an inventory.

    Args:
        inventory_id: Target inventory ID.
        hostname: FQDN of the host to add.
        enabled: Whether the host is enabled (default True).
    """
    if inventory_id not in _ENV_HOSTS:
        return {"error": f"Inventory {inventory_id} not found"}

    existing = [h for h in _ENV_HOSTS[inventory_id] if h["name"] == hostname]
    if existing:
        return {"status": "already_exists", "host": existing[0]}

    new_id = max(h["id"] for h in _ENV_HOSTS[inventory_id]) + 1
    new_host = {
        "id": new_id,
        "name": hostname,
        "enabled": enabled,
        "has_active_failures": False,
        "inventory": inventory_id,
    }
    _ENV_HOSTS[inventory_id].append(new_host)
    return {"status": "created", "host": new_host}


# ---- Job Management ----

@mcp.tool
def list_job_templates(
    search: Optional[str] = None,
) -> dict:
    """List available job templates, optionally filtered by search term.

    Args:
        search: Optional search string to filter templates by name or CVE ID.
    """
    results = MOCK_JOB_TEMPLATES
    if search:
        term = search.lower()
        results = [t for t in results if term in t["name"].lower() or term in t.get("cve_id", "").lower()]

    return {
        "count": len(results),
        "results": results,
    }


@mcp.tool
def launch_job(
    job_template_id: int,
    inventory_id: Optional[int] = None,
    limit: Optional[str] = None,
    extra_vars: Optional[dict] = None,
) -> dict:
    """Launch a job from a job template.

    Args:
        job_template_id: ID of the job template to launch.
        inventory_id: Override inventory (uses template default if omitted).
        limit: Host pattern to limit execution scope.
        extra_vars: Additional variables to pass to the playbook.
    """
    global _next_job_id

    if job_template_id not in TEMPLATE_BY_ID:
        return {"error": f"Job template {job_template_id} not found"}

    template = TEMPLATE_BY_ID[job_template_id]
    inv_id = inventory_id or template["inventory"]

    target_hosts = []
    if inv_id in _ENV_HOSTS:
        hosts = _ENV_HOSTS[inv_id]
        if limit:
            target_hosts = [h["name"] for h in hosts if limit.lower() in h["name"].lower()]
        else:
            target_hosts = [h["name"] for h in hosts]

    job_id = _next_job_id
    _next_job_id += 1

    started = REFERENCE_TIME.isoformat() + "Z"
    finished = (REFERENCE_TIME + timedelta(minutes=3, seconds=42)).isoformat() + "Z"

    job = {
        "id": job_id,
        "name": template["name"],
        "job_template": job_template_id,
        "inventory": inv_id,
        "status": "successful",
        "started": started,
        "finished": finished,
        "elapsed": 222.0,
        "target_hosts": target_hosts,
        "host_count": len(target_hosts),
        "cve_id": template.get("cve_id", ""),
        "limit": limit,
        "extra_vars": extra_vars or {},
        "failed": False,
    }
    _launched_jobs[job_id] = job

    return {
        "job_id": job_id,
        "status": "successful",
        "url": f"https://aap.example.com/#/jobs/playbook/{job_id}",
        "started": started,
        "finished": finished,
        "host_count": len(target_hosts),
    }


@mcp.tool
def get_job_status(job_id: int) -> dict:
    """Get the status and details of a launched job.

    Args:
        job_id: The job ID returned by launch_job.
    """
    if job_id not in _launched_jobs:
        return {"error": f"Job {job_id} not found"}
    job = _launched_jobs[job_id]
    return {
        "id": job["id"],
        "name": job["name"],
        "status": job["status"],
        "started": job["started"],
        "finished": job["finished"],
        "elapsed": job["elapsed"],
        "host_count": job["host_count"],
        "failed": job["failed"],
    }


@mcp.tool
def get_job_log(job_id: int) -> dict:
    """Get the stdout log of a completed job.

    Args:
        job_id: The job ID returned by launch_job.
    """
    if job_id not in _launched_jobs:
        return {"error": f"Job {job_id} not found"}
    job = _launched_jobs[job_id]
    return {
        "id": job_id,
        "status": job["status"],
        "stdout": _generate_job_log(job),
    }


if __name__ == "__main__":
    mcp.run()
