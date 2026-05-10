#!/usr/bin/env python3
"""
Mock Red Hat Security MCP Server.

Simulates the red-hat-security MCP (https://security-mcp.api.redhat.com/mcp)
with cve-mcp and advisories-mcp tool groups.

Simulated CVEs:
  CVE-2024-6387  (Critical, OpenSSH regreSSHion, RHEL 9)
  CVE-2024-3094  (Critical, xz backdoor, RHEL 9 + Fedora)
  CVE-2024-21626 (Important, runc container escape, OCP)
  CVE-2023-44487 (Important, HTTP/2 Rapid Reset, multiple)
  CVE-2024-9999  (Moderate, demo flaw, no advisory yet)
"""

import json
from fastmcp import FastMCP

mcp = FastMCP("red-hat-security")

CVES = {
    "CVE-2024-6387": {
        "id": "CVE-2024-6387",
        "title": "OpenSSH: regreSSHion — Remote Unauthenticated Code Execution",
        "description": (
            "A signal handler race condition was found in OpenSSH's sshd server. "
            "If a client does not authenticate within LoginGraceTime seconds (120 by "
            "default), sshd's SIGALRM handler is called asynchronously, invoking "
            "functions that are not async-signal-safe (e.g., syslog()). An unauthenticated "
            "remote attacker can exploit this to achieve remote code execution as root."
        ),
        "severity": "Critical",
        "cvss3_score": 8.1,
        "cvss3_vector": "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "nvd_cvss3_score": 8.1,
        "cwe": "CWE-364",
        "public_date": "2024-07-01T00:00:00Z",
        "affected_products": [
            {"product": "Red Hat Enterprise Linux 9", "status": "Fixed", "errata": "RHSA-2024:4312"},
            {"product": "Red Hat Enterprise Linux 8", "status": "Not affected"},
            {"product": "Red Hat Enterprise Linux 7", "status": "Not affected"},
        ],
        "advisories": ["RHSA-2024:4312"],
        "mitigation": (
            "As an immediate mitigation, set LoginGraceTime to 0 in /etc/ssh/sshd_config "
            "and restart sshd. This prevents the race condition but exposes the server to "
            "MaxStartups exhaustion denial of service."
        ),
    },
    "CVE-2024-3094": {
        "id": "CVE-2024-3094",
        "title": "xz/liblzma: Malicious Backdoor in xz-utils",
        "description": (
            "Malicious code was discovered in the upstream xz tarballs starting from "
            "version 5.6.0. The backdoor manipulates the build process of liblzma via "
            "a series of complex obfuscations to modify specific functions in the "
            "resulting library. This results in a modified liblzma that can intercept "
            "and modify data interaction with the OpenSSH server process (sshd), "
            "allowing unauthorized remote access."
        ),
        "severity": "Critical",
        "cvss3_score": 10.0,
        "cvss3_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H",
        "nvd_cvss3_score": 10.0,
        "cwe": "CWE-506",
        "public_date": "2024-03-29T00:00:00Z",
        "affected_products": [
            {"product": "Red Hat Enterprise Linux 9", "status": "Not affected",
             "detail": "RHEL 9 ships xz 5.2.5 which predates the backdoor"},
            {"product": "Fedora 40", "status": "Fixed", "errata": "FEDORA-2024-d02c7bb266"},
            {"product": "Fedora 41 (Rawhide)", "status": "Fixed", "errata": "FEDORA-2024-e4e90478f5"},
        ],
        "advisories": ["RHSA-2024:1640"],
        "mitigation": (
            "Downgrade xz to version 5.4.x or earlier. On affected Fedora systems: "
            "dnf downgrade xz xz-libs."
        ),
    },
    "CVE-2024-21626": {
        "id": "CVE-2024-21626",
        "title": "runc: Container Breakout via Leaked File Descriptor",
        "description": (
            "A flaw was found in runc where an attacker can exploit a file descriptor "
            "leak from /proc/self/fd to gain access to the host filesystem from within "
            "a container. A malicious container image or Dockerfile could use a leaked "
            "fd from the host during container startup to 'break out' of the container."
        ),
        "severity": "Important",
        "cvss3_score": 8.6,
        "cvss3_vector": "CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H",
        "nvd_cvss3_score": 8.6,
        "cwe": "CWE-668",
        "public_date": "2024-01-31T00:00:00Z",
        "affected_products": [
            {"product": "Red Hat OpenShift Container Platform 4.14", "status": "Fixed",
             "errata": "RHSA-2024:0670"},
            {"product": "Red Hat OpenShift Container Platform 4.13", "status": "Fixed",
             "errata": "RHSA-2024:0671"},
            {"product": "Red Hat Enterprise Linux 9", "status": "Fixed",
             "errata": "RHSA-2024:0752"},
        ],
        "advisories": ["RHSA-2024:0670", "RHSA-2024:0671", "RHSA-2024:0752"],
        "mitigation": (
            "Red Hat recommends applying the errata fix. As a temporary measure, "
            "use SELinux enforcement to limit the impact of container breakout."
        ),
    },
    "CVE-2023-44487": {
        "id": "CVE-2023-44487",
        "title": "HTTP/2: Rapid Reset Attack",
        "description": (
            "A flaw was found in handling multiplexed streams in the HTTP/2 protocol. "
            "A client can rapidly create and cancel requests, causing excessive server "
            "resource consumption. This results in denial of service attacks on HTTP/2 "
            "servers without requiring a large volume of traffic."
        ),
        "severity": "Important",
        "cvss3_score": 7.5,
        "cvss3_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H",
        "nvd_cvss3_score": 7.5,
        "cwe": "CWE-400",
        "public_date": "2023-10-10T00:00:00Z",
        "affected_products": [
            {"product": "Red Hat Enterprise Linux 9", "status": "Fixed",
             "errata": "RHSA-2023:5837"},
            {"product": "Red Hat Enterprise Linux 8", "status": "Fixed",
             "errata": "RHSA-2023:5838"},
            {"product": "Red Hat OpenShift Container Platform 4.14", "status": "Fixed",
             "errata": "RHSA-2023:6839"},
            {"product": "Red Hat JBoss Enterprise Application Platform 7", "status": "Fixed",
             "errata": "RHSA-2023:5928"},
        ],
        "advisories": [
            "RHSA-2023:5837", "RHSA-2023:5838", "RHSA-2023:6839", "RHSA-2023:5928",
        ],
        "mitigation": (
            "For RHEL/OCP: apply the errata. For JBoss EAP: upgrade to patched version "
            "or configure HTTP/2 connection limits."
        ),
    },
    "CVE-2024-9999": {
        "id": "CVE-2024-9999",
        "title": "Demo: Buffer over-read in example-lib",
        "description": (
            "A buffer over-read vulnerability was found in example-lib's input parser. "
            "Specially crafted input can cause a read beyond the allocated buffer, "
            "potentially leaking sensitive information from server memory."
        ),
        "severity": "Moderate",
        "cvss3_score": 5.3,
        "cvss3_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N",
        "nvd_cvss3_score": 6.5,
        "cwe": "CWE-125",
        "public_date": "2024-11-15T00:00:00Z",
        "affected_products": [
            {"product": "Red Hat Enterprise Linux 9", "status": "Under investigation"},
            {"product": "Red Hat Enterprise Linux 8", "status": "Under investigation"},
        ],
        "advisories": [],
        "mitigation": (
            "No fix is currently available. Red Hat is investigating. As a workaround, "
            "restrict network access to the affected service."
        ),
    },
}

ADVISORIES = {
    "RHSA-2024:4312": {
        "id": "RHSA-2024:4312",
        "type": "RHSA",
        "title": "Important: openssh security update",
        "severity": "Critical",
        "synopsis": "An update for openssh is now available for Red Hat Enterprise Linux 9.",
        "description": (
            "OpenSSH is an SSH protocol implementation supported by a number of Linux, "
            "UNIX, and similar operating systems. This update fixes CVE-2024-6387 "
            "(regreSSHion) — a signal handler race condition in sshd."
        ),
        "cves": ["CVE-2024-6387"],
        "published_date": "2024-07-03T00:00:00Z",
        "affected_products": ["Red Hat Enterprise Linux 9"],
        "solution": (
            "For details on how to apply this update, refer to:\n"
            "https://access.redhat.com/articles/11258\n\n"
            "After installing the update, restart the sshd service:\n"
            "  systemctl restart sshd"
        ),
    },
    "RHSA-2024:1640": {
        "id": "RHSA-2024:1640",
        "type": "RHSA",
        "title": "Critical: xz security update",
        "severity": "Critical",
        "synopsis": "An update for xz is now available.",
        "description": (
            "XZ Utils provides data compression/decompression. This update addresses "
            "CVE-2024-3094 — malicious code injected into the xz build process."
        ),
        "cves": ["CVE-2024-3094"],
        "published_date": "2024-04-01T00:00:00Z",
        "affected_products": ["Fedora 40", "Fedora 41"],
        "solution": (
            "For details on how to apply this update, refer to:\n"
            "https://access.redhat.com/articles/11258\n\n"
            "On affected Fedora systems:\n"
            "  dnf update xz xz-libs"
        ),
    },
    "RHSA-2024:0670": {
        "id": "RHSA-2024:0670",
        "type": "RHSA",
        "title": "Important: runc security update for OpenShift Container Platform 4.14",
        "severity": "Important",
        "synopsis": "An update for runc is now available for OCP 4.14.",
        "description": (
            "The runC tool is a lightweight, portable implementation of the Open "
            "Container Format (OCF). This update fixes CVE-2024-21626 — a container "
            "breakout via leaked file descriptor."
        ),
        "cves": ["CVE-2024-21626"],
        "published_date": "2024-02-05T00:00:00Z",
        "affected_products": ["Red Hat OpenShift Container Platform 4.14"],
        "solution": (
            "For OpenShift Container Platform 4.14, see the following documentation:\n"
            "https://docs.openshift.com/container-platform/4.14/updating/updating_a_cluster/updating-cluster-cli.html\n\n"
            "  oc adm upgrade --to-latest=true"
        ),
    },
    "RHSA-2024:0671": {
        "id": "RHSA-2024:0671",
        "type": "RHSA",
        "title": "Important: runc security update for OpenShift Container Platform 4.13",
        "severity": "Important",
        "synopsis": "An update for runc is now available for OCP 4.13.",
        "description": "Fixes CVE-2024-21626 for OCP 4.13.",
        "cves": ["CVE-2024-21626"],
        "published_date": "2024-02-05T00:00:00Z",
        "affected_products": ["Red Hat OpenShift Container Platform 4.13"],
        "solution": "Apply the OCP 4.13 update via oc adm upgrade.",
    },
    "RHSA-2024:0752": {
        "id": "RHSA-2024:0752",
        "type": "RHSA",
        "title": "Important: runc security update for RHEL 9",
        "severity": "Important",
        "synopsis": "An update for runc is now available for RHEL 9.",
        "description": "Fixes CVE-2024-21626 for RHEL 9.",
        "cves": ["CVE-2024-21626"],
        "published_date": "2024-02-08T00:00:00Z",
        "affected_products": ["Red Hat Enterprise Linux 9"],
        "solution": "dnf update runc",
    },
    "RHSA-2023:5837": {
        "id": "RHSA-2023:5837",
        "type": "RHSA",
        "title": "Important: nghttp2 security update for RHEL 9",
        "severity": "Important",
        "synopsis": "An update for nghttp2 is now available for RHEL 9.",
        "description": "Fixes CVE-2023-44487 (HTTP/2 Rapid Reset) for RHEL 9.",
        "cves": ["CVE-2023-44487"],
        "published_date": "2023-10-18T00:00:00Z",
        "affected_products": ["Red Hat Enterprise Linux 9"],
        "solution": "dnf update nghttp2",
    },
    "RHSA-2023:5838": {
        "id": "RHSA-2023:5838",
        "type": "RHSA",
        "title": "Important: nghttp2 security update for RHEL 8",
        "severity": "Important",
        "synopsis": "An update for nghttp2 is now available for RHEL 8.",
        "description": "Fixes CVE-2023-44487 for RHEL 8.",
        "cves": ["CVE-2023-44487"],
        "published_date": "2023-10-18T00:00:00Z",
        "affected_products": ["Red Hat Enterprise Linux 8"],
        "solution": "dnf update nghttp2",
    },
    "RHSA-2023:6839": {
        "id": "RHSA-2023:6839",
        "type": "RHSA",
        "title": "Important: OpenShift Container Platform 4.14 security update",
        "severity": "Important",
        "synopsis": "Fixes CVE-2023-44487 for OCP 4.14.",
        "description": "Fixes HTTP/2 Rapid Reset for OCP 4.14.",
        "cves": ["CVE-2023-44487"],
        "published_date": "2023-11-08T00:00:00Z",
        "affected_products": ["Red Hat OpenShift Container Platform 4.14"],
        "solution": "oc adm upgrade --to-latest=true",
    },
    "RHSA-2023:5928": {
        "id": "RHSA-2023:5928",
        "type": "RHSA",
        "title": "Important: JBoss EAP 7 security update",
        "severity": "Important",
        "synopsis": "Fixes CVE-2023-44487 for JBoss EAP 7.",
        "description": "Fixes HTTP/2 Rapid Reset for JBoss EAP 7.",
        "cves": ["CVE-2023-44487"],
        "published_date": "2023-10-25T00:00:00Z",
        "affected_products": ["Red Hat JBoss Enterprise Application Platform 7"],
        "solution": "Upgrade to JBoss EAP 7.4.14 or later.",
    },
}


@mcp.tool()
def cve_detail(cve_id: str) -> str:
    """Get detailed CVE metadata from Red Hat Security."""
    cve = CVES.get(cve_id.upper())
    if not cve:
        return json.dumps({"error": f"CVE {cve_id} not found in Red Hat database"})
    return json.dumps(cve)


@mcp.tool()
def map_cve_advisories(cve_id: str) -> str:
    """Map a CVE to its linked Red Hat advisories (RHSA/RHBA/RHEA)."""
    cve = CVES.get(cve_id.upper())
    if not cve:
        return json.dumps({"error": f"CVE {cve_id} not found"})
    adv_ids = cve.get("advisories", [])
    result = []
    for aid in adv_ids:
        adv = ADVISORIES.get(aid)
        if adv:
            result.append({
                "id": adv["id"],
                "type": adv["type"],
                "title": adv["title"],
                "severity": adv["severity"],
                "published_date": adv["published_date"],
            })
    return json.dumps({"cve_id": cve_id.upper(), "advisories": result})


@mcp.tool()
def get_advisory_solution(advisory_id: str) -> str:
    """Get remediation steps for a specific Red Hat advisory."""
    adv = ADVISORIES.get(advisory_id.upper())
    if not adv:
        return json.dumps({"error": f"Advisory {advisory_id} not found"})
    return json.dumps({
        "id": adv["id"],
        "solution": adv["solution"],
        "affected_products": adv["affected_products"],
    })


@mcp.tool()
def summarize_advisory(advisory_id: str) -> str:
    """Get a brief summary of a Red Hat advisory."""
    adv = ADVISORIES.get(advisory_id.upper())
    if not adv:
        return json.dumps({"error": f"Advisory {advisory_id} not found"})
    return json.dumps({
        "id": adv["id"],
        "type": adv["type"],
        "title": adv["title"],
        "severity": adv["severity"],
        "synopsis": adv["synopsis"],
        "description": adv["description"],
        "cves": adv["cves"],
        "published_date": adv["published_date"],
    })


if __name__ == "__main__":
    mcp.run()
