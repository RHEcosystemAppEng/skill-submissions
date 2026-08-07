#!/usr/bin/env python3
"""
Mock Assisted Installer MCP Server for OpenShift cluster management.

Simulates both:
  - openshift-self-managed (Assisted Installer API for OCP/SNO)
  - openshift-ocm-managed (OCM API for ROSA/ARO/OSD)

Provides tools used by /cluster-creator and /cluster-inventory skills.
"""

import json
import uuid
from typing import Optional

from fastmcp import FastMCP

mcp = FastMCP("openshift-self-managed")

NOW = "2026-05-01T10:00:00Z"

VERSIONS = [
    {"display_name": "4.16.3", "support_level": "production"},
    {"display_name": "4.16.2", "support_level": "production"},
    {"display_name": "4.15.12", "support_level": "production"},
    {"display_name": "4.15.11", "support_level": "production"},
    {"display_name": "4.14.18", "support_level": "maintenance"},
]

CLUSTERS = [
    {
        "id": "c1a2b3c4-0001-4000-8000-000000000001",
        "name": "prod-ocp-east",
        "status": "installed",
        "openshift_version": "4.16.3",
        "platform": {"type": "baremetal"},
        "high_availability_mode": "Full",
        "base_dns_domain": "example.com",
        "api_vips": [{"ip": "10.0.1.100"}],
        "ingress_vips": [{"ip": "10.0.1.101"}],
        "created_at": "2026-03-15T08:00:00Z",
        "installed_at": "2026-03-15T12:30:00Z",
        "host_count": 6,
        "hosts": [
            {"id": "h001", "requested_hostname": "master-0", "role": "master", "status": "installed",
             "inventory": {"cpu": {"count": 16}, "memory": {"physical_bytes": 68719476736}}},
            {"id": "h002", "requested_hostname": "master-1", "role": "master", "status": "installed",
             "inventory": {"cpu": {"count": 16}, "memory": {"physical_bytes": 68719476736}}},
            {"id": "h003", "requested_hostname": "master-2", "role": "master", "status": "installed",
             "inventory": {"cpu": {"count": 16}, "memory": {"physical_bytes": 68719476736}}},
            {"id": "h004", "requested_hostname": "worker-0", "role": "worker", "status": "installed",
             "inventory": {"cpu": {"count": 32}, "memory": {"physical_bytes": 137438953472}}},
            {"id": "h005", "requested_hostname": "worker-1", "role": "worker", "status": "installed",
             "inventory": {"cpu": {"count": 32}, "memory": {"physical_bytes": 137438953472}}},
            {"id": "h006", "requested_hostname": "worker-2", "role": "worker", "status": "installed",
             "inventory": {"cpu": {"count": 32}, "memory": {"physical_bytes": 137438953472}}},
        ],
    },
    {
        "id": "c1a2b3c4-0002-4000-8000-000000000002",
        "name": "edge-sno-01",
        "status": "installed",
        "openshift_version": "4.15.12",
        "platform": {"type": "none"},
        "high_availability_mode": "None",
        "base_dns_domain": "edge.example.com",
        "api_vips": [],
        "ingress_vips": [],
        "created_at": "2026-04-01T10:00:00Z",
        "installed_at": "2026-04-01T11:45:00Z",
        "host_count": 1,
        "hosts": [
            {"id": "h010", "requested_hostname": "sno-node", "role": "master", "status": "installed",
             "inventory": {"cpu": {"count": 16}, "memory": {"physical_bytes": 68719476736}}},
        ],
    },
    {
        "id": "c1a2b3c4-0003-4000-8000-000000000003",
        "name": "staging-cluster",
        "status": "installing",
        "openshift_version": "4.16.3",
        "platform": {"type": "vsphere"},
        "high_availability_mode": "Full",
        "base_dns_domain": "staging.example.com",
        "api_vips": [{"ip": "10.0.2.100"}],
        "ingress_vips": [{"ip": "10.0.2.101"}],
        "created_at": "2026-05-01T08:00:00Z",
        "host_count": 3,
        "hosts": [
            {"id": "h020", "requested_hostname": "master-0", "role": "master", "status": "installing",
             "inventory": {"cpu": {"count": 8}, "memory": {"physical_bytes": 34359738368}}},
            {"id": "h021", "requested_hostname": "master-1", "role": "master", "status": "installing",
             "inventory": {"cpu": {"count": 8}, "memory": {"physical_bytes": 34359738368}}},
            {"id": "h022", "requested_hostname": "master-2", "role": "master", "status": "installing",
             "inventory": {"cpu": {"count": 8}, "memory": {"physical_bytes": 34359738368}}},
        ],
    },
]

OCM_CLUSTERS = [
    {
        "id": "ocm-rosa-001",
        "name": "rosa-prod-us",
        "state": "ready",
        "openshift_version": "4.16.2",
        "cloud_provider": {"id": "aws"},
        "region": {"id": "us-east-1"},
        "product": {"id": "rosa"},
        "creation_timestamp": "2026-02-10T14:00:00Z",
        "nodes": {"compute": 3, "master": 3},
    },
    {
        "id": "ocm-aro-001",
        "name": "aro-eu-west",
        "state": "ready",
        "openshift_version": "4.15.12",
        "cloud_provider": {"id": "azure"},
        "region": {"id": "westeurope"},
        "product": {"id": "aro"},
        "creation_timestamp": "2026-03-20T09:00:00Z",
        "nodes": {"compute": 2, "master": 3},
    },
]

EVENTS = {
    "c1a2b3c4-0003-4000-8000-000000000003": [
        {"event_time": "2026-05-01T08:01:00Z", "severity": "info", "message": "Cluster staging-cluster created"},
        {"event_time": "2026-05-01T08:05:00Z", "severity": "info", "message": "Generated discovery ISO for staging-cluster"},
        {"event_time": "2026-05-01T08:30:00Z", "severity": "info", "message": "Host master-0 discovered and validated"},
        {"event_time": "2026-05-01T08:31:00Z", "severity": "info", "message": "Host master-1 discovered and validated"},
        {"event_time": "2026-05-01T08:32:00Z", "severity": "info", "message": "Host master-2 discovered and validated"},
        {"event_time": "2026-05-01T09:00:00Z", "severity": "info", "message": "Installation triggered for staging-cluster"},
        {"event_time": "2026-05-01T09:15:00Z", "severity": "info", "message": "Bootstrap node initialized, writing ignition configs"},
        {"event_time": "2026-05-01T09:45:00Z", "severity": "warning", "message": "Waiting for control plane to stabilize..."},
    ],
    "c1a2b3c4-0001-4000-8000-000000000001": [
        {"event_time": "2026-03-15T08:01:00Z", "severity": "info", "message": "Cluster prod-ocp-east created"},
        {"event_time": "2026-03-15T12:30:00Z", "severity": "info", "message": "Cluster installation completed successfully"},
    ],
}


def _find_cluster(cluster_id: str) -> dict:
    for c in CLUSTERS:
        if c["id"] == cluster_id or c["name"] == cluster_id:
            return c
    raise ValueError(f"Cluster not found: {cluster_id}")


@mcp.tool()
def list_versions() -> str:
    """List available OpenShift versions for cluster creation."""
    return json.dumps(VERSIONS, indent=2)


@mcp.tool()
def list_clusters() -> str:
    """List all clusters managed by the Assisted Installer service."""
    summary = []
    for c in CLUSTERS:
        summary.append({
            "id": c["id"],
            "name": c["name"],
            "status": c["status"],
            "openshift_version": c["openshift_version"],
            "platform": c["platform"]["type"],
            "ha_mode": c["high_availability_mode"],
            "host_count": c["host_count"],
            "created_at": c["created_at"],
        })
    return json.dumps(summary, indent=2)


@mcp.tool()
def cluster_info(cluster_id: str) -> str:
    """Get detailed information about a specific cluster."""
    c = _find_cluster(cluster_id)
    return json.dumps(c, indent=2)


@mcp.tool()
def cluster_events(cluster_id: str) -> str:
    """Get events for a cluster (useful for monitoring installation progress)."""
    c = _find_cluster(cluster_id)
    events = EVENTS.get(c["id"], [])
    if not events:
        return json.dumps([{"event_time": NOW, "severity": "info",
                            "message": f"No recent events for cluster {c['name']}"}])
    return json.dumps(events, indent=2)


@mcp.tool()
def create_cluster(
    name: str,
    openshift_version: str,
    high_availability_mode: str = "Full",
    base_dns_domain: str = "example.com",
    platform_type: str = "baremetal",
) -> str:
    """Create a new cluster definition in the Assisted Installer."""
    new_id = str(uuid.uuid4())
    cluster = {
        "id": new_id,
        "name": name,
        "status": "pending-for-input",
        "openshift_version": openshift_version,
        "platform": {"type": platform_type},
        "high_availability_mode": high_availability_mode,
        "base_dns_domain": base_dns_domain,
        "api_vips": [],
        "ingress_vips": [],
        "created_at": NOW,
        "host_count": 0,
        "hosts": [],
    }
    return json.dumps(cluster, indent=2)


@mcp.tool()
def set_cluster_vips(cluster_id: str, api_vip: str, ingress_vip: str) -> str:
    """Set API and Ingress VIPs for an HA cluster."""
    c = _find_cluster(cluster_id)
    return json.dumps({
        "status": "success",
        "cluster": c["name"],
        "api_vips": [{"ip": api_vip}],
        "ingress_vips": [{"ip": ingress_vip}],
    })


@mcp.tool()
def set_host_role(cluster_id: str, host_id: str, role: str) -> str:
    """Assign a role (master/worker) to a discovered host."""
    c = _find_cluster(cluster_id)
    if role not in ("master", "worker", "auto-assign"):
        raise ValueError(f"Invalid role: {role}. Must be master, worker, or auto-assign")
    return json.dumps({
        "status": "success",
        "cluster": c["name"],
        "host_id": host_id,
        "role": role,
    })


@mcp.tool()
def cluster_iso_download_url(cluster_id: str) -> str:
    """Get the discovery ISO download URL for a cluster."""
    c = _find_cluster(cluster_id)
    return json.dumps({
        "url": f"https://assisted-installer.example.com/api/v2/infra-envs/{c['id']}/downloads/image",
        "expires_at": "2026-05-02T10:00:00Z",
    })


@mcp.tool()
def install_cluster(cluster_id: str) -> str:
    """Trigger cluster installation. Requires all validations to pass first."""
    c = _find_cluster(cluster_id)
    return json.dumps({
        "status": "preparing-for-installation",
        "cluster": c["name"],
        "message": f"Installation triggered for {c['name']}. Monitor with cluster_events.",
    })


@mcp.tool()
def cluster_credentials_download_url(cluster_id: str) -> str:
    """Get the kubeconfig/credentials download URL for an installed cluster."""
    c = _find_cluster(cluster_id)
    if c["status"] != "installed":
        raise ValueError(f"Cluster {c['name']} is not yet installed (status: {c['status']})")
    return json.dumps({
        "url": f"https://assisted-installer.example.com/api/v2/clusters/{c['id']}/downloads/credentials",
        "files": ["kubeconfig", "kubeadmin-password"],
    })


@mcp.tool()
def cluster_logs_download_url(cluster_id: str) -> str:
    """Get the logs download URL for a cluster."""
    c = _find_cluster(cluster_id)
    return json.dumps({
        "url": f"https://assisted-installer.example.com/api/v2/clusters/{c['id']}/logs",
    })


@mcp.tool()
def list_static_network_config(cluster_id: str) -> str:
    """List static network configurations for a cluster."""
    return json.dumps({"network_configs": [], "message": "No static network configuration set"})


@mcp.tool()
def generate_nmstate_yaml(
    interface_name: str,
    ip_address: str,
    prefix_length: int = 24,
    gateway: str = "",
    dns_servers: str = "",
) -> str:
    """Generate NMState YAML for static network configuration."""
    return json.dumps({
        "yaml": f"""interfaces:
  - name: {interface_name}
    type: ethernet
    state: up
    ipv4:
      enabled: true
      address:
        - ip: {ip_address}
          prefix-length: {prefix_length}
      dhcp: false
routes:
  config:
    - destination: 0.0.0.0/0
      next-hop-address: {gateway or '10.0.0.1'}
      next-hop-interface: {interface_name}
dns-resolver:
  config:
    server:
      - {dns_servers or '8.8.8.8'}""",
        "valid": True,
    })


@mcp.tool()
def validate_nmstate_yaml(yaml_content: str) -> str:
    """Validate NMState YAML configuration."""
    return json.dumps({"valid": True, "message": "NMState YAML is valid"})


@mcp.tool()
def alter_static_network_config_nmstate_for_host(
    cluster_id: str,
    host_id: str,
    nmstate_yaml: str,
    mac_address: str,
) -> str:
    """Apply static network config (NMState) to a specific host."""
    return json.dumps({
        "status": "success",
        "message": f"Static network config applied to host {host_id}",
    })


if __name__ == "__main__":
    mcp.run(transport="stdio")
