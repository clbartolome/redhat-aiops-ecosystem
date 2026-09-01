#!/usr/bin/env python3
"""Generate the AIOps VM Fleet Grafana dashboard ConfigMap."""

from __future__ import annotations

import json
from pathlib import Path

# Expected demo fleet size; sizes the VM table panel height (header + rows + padding).
VM_FLEET_SIZE = 3

NS = "{{ aap_casc.aiops_demo_namespace }}"
OBS_NS = "{{ observability.namespace }}"

THRESHOLDS_PCT = {
    "mode": "absolute",
    "steps": [
        {"color": "green", "value": None},
        {"color": "#EAB839", "value": 70},
        {"color": "red", "value": 90},
    ],
}

THRESHOLDS_IOPS = {
    "mode": "absolute",
    "steps": [
        {"color": "green", "value": None},
        {"color": "#EAB839", "value": 500},
        {"color": "red", "value": 2000},
    ],
}

THRESHOLDS_NETWORK = {
    "mode": "absolute",
    "steps": [
        {"color": "green", "value": None},
        {"color": "#EAB839", "value": 1048576},
        {"color": "red", "value": 10485760},
    ],
}

THRESHOLDS_LATENCY = {
    "mode": "absolute",
    "steps": [
        {"color": "green", "value": None},
        {"color": "#EAB839", "value": 0.1},
        {"color": "red", "value": 0.5},
    ],
}

THRESHOLDS_UP = {
    "mode": "absolute",
    "steps": [
        {"color": "red", "value": None},
        {"color": "green", "value": 1},
    ],
}

STATUS_MAPPINGS = [
    {"type": "value", "options": {"0": {"color": "red", "text": "🔴 Critical", "index": 0}}},
    {"type": "value", "options": {"1": {"color": "green", "text": "🟢 OK", "index": 1}}},
    {"type": "value", "options": {"2": {"color": "#EAB839", "text": "🟡 Warning", "index": 2}}},
]

SERVICE_MAPPINGS = [
    {"type": "value", "options": {"0": {"color": "red", "text": "🔴 Down", "index": 0}}},
    {"type": "value", "options": {"1": {"color": "green", "text": "🟢 Up", "index": 1}}},
]

ALERT_MAPPINGS = [
    {"type": "range", "options": {"from": 0, "to": 0.5, "result": {"color": "green", "text": "🟢 0", "index": 0}}},
    {"type": "range", "options": {"from": 0.5, "to": 1.5, "result": {"color": "#EAB839", "text": "🟡", "index": 1}}},
    {"type": "range", "options": {"from": 1.5, "to": 1000, "result": {"color": "red", "text": "🔴", "index": 2}}},
]


def cell_bg() -> dict:
    return {"type": "color-background"}


def status_expr() -> str:
    return (
        f'((count by (name) (label_replace(ALERTS{{alertstate="firing",vm_name!=""}}, "name", "$1", "vm_name", "(.*)")) > bool 0) * 0) '
        f'or ((label_replace(probe_success{{job="apache-http"}}, "name", "$1", "vm_name", "(.*)") == bool 0) * 2) '
        f'or ((label_replace(probe_success{{job="apache-http"}}, "name", "$1", "vm_name", "(.*)") == bool 1) * 1) '
        f'or ((group by (name) (kubevirt_vmi_memory_available_bytes{{namespace="{NS}"}})) * 0 + 1)'
    )


def vm_table_panel(*, grid_y: int, grid_h: int) -> dict:
    return {
        "type": "table",
        "title": "Virtual Machine Fleet Status",
        "description": "Consolidated view of CPU, memory, disk, IOPS, network, latency, service availability and active alerts per VM.",
        "id": 1,
        "gridPos": {"h": grid_h, "w": 24, "x": 0, "y": grid_y},
        "datasource": {"type": "prometheus", "uid": "prometheus"},
        "fieldConfig": {
            "defaults": {
                "custom": {"align": "center", "cellOptions": {"type": "auto"}, "inspect": False},
                "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}]},
            },
            "overrides": [
                {"matcher": {"id": "byName", "options": "VM"}, "properties": [
                    {"id": "custom.width", "value": 150},
                    {"id": "custom.align", "value": "left"},
                ]},
                {"matcher": {"id": "byName", "options": "Status"}, "properties": [
                    {"id": "mappings", "value": STATUS_MAPPINGS},
                    {"id": "custom.cellOptions", "value": cell_bg()},
                ]},
                {"matcher": {"id": "byName", "options": "CPU %"}, "properties": [
                    {"id": "unit", "value": "percent"},
                    {"id": "decimals", "value": 1},
                    {"id": "thresholds", "value": THRESHOLDS_PCT},
                    {"id": "custom.cellOptions", "value": cell_bg()},
                ]},
                {"matcher": {"id": "byName", "options": "Memory %"}, "properties": [
                    {"id": "unit", "value": "percent"},
                    {"id": "decimals", "value": 1},
                    {"id": "thresholds", "value": THRESHOLDS_PCT},
                    {"id": "custom.cellOptions", "value": cell_bg()},
                ]},
                {"matcher": {"id": "byName", "options": "Disk %"}, "properties": [
                    {"id": "unit", "value": "percent"},
                    {"id": "decimals", "value": 1},
                    {"id": "thresholds", "value": THRESHOLDS_PCT},
                    {"id": "custom.cellOptions", "value": cell_bg()},
                ]},
                {"matcher": {"id": "byName", "options": "IOPS"}, "properties": [
                    {"id": "decimals", "value": 1},
                    {"id": "thresholds", "value": THRESHOLDS_IOPS},
                    {"id": "custom.cellOptions", "value": cell_bg()},
                ]},
                {"matcher": {"id": "byName", "options": "Network"}, "properties": [
                    {"id": "unit", "value": "Bps"},
                    {"id": "decimals", "value": 1},
                    {"id": "thresholds", "value": THRESHOLDS_NETWORK},
                    {"id": "custom.cellOptions", "value": cell_bg()},
                ]},
                {"matcher": {"id": "byName", "options": "Latency"}, "properties": [
                    {"id": "unit", "value": "s"},
                    {"id": "decimals", "value": 3},
                    {"id": "thresholds", "value": THRESHOLDS_LATENCY},
                    {"id": "custom.cellOptions", "value": cell_bg()},
                ]},
                {"matcher": {"id": "byName", "options": "Service"}, "properties": [
                    {"id": "mappings", "value": SERVICE_MAPPINGS},
                    {"id": "custom.cellOptions", "value": cell_bg()},
                ]},
                {"matcher": {"id": "byName", "options": "Active Alerts"}, "properties": [
                    {"id": "decimals", "value": 0},
                    {"id": "mappings", "value": ALERT_MAPPINGS},
                    {"id": "custom.cellOptions", "value": cell_bg()},
                ]},
            ],
        },
        "options": {
            "showHeader": True,
            "cellHeight": "sm",
            "footer": {"show": False, "reducer": ["sum"], "countRows": False},
            "sortBy": [{"displayName": "VM", "desc": False}],
        },
        "pluginVersion": "11.3.0",
        "targets": [
            {"refId": "CPU", "expr": f'100 * sum by (name) (rate(kubevirt_vmi_cpu_usage_seconds_total{{namespace="{NS}"}}[5m])) / sum by (name) (kubevirt_vmi_vcpu_seconds_total{{namespace="{NS}"}})', "format": "table", "instant": True},
            {"refId": "MEM", "expr": f'100 * sum by (name) (kubevirt_vmi_memory_domain_bytes{{namespace="{NS}"}} - kubevirt_vmi_memory_available_bytes{{namespace="{NS}"}}) / sum by (name) (kubevirt_vmi_memory_domain_bytes{{namespace="{NS}"}})', "format": "table", "instant": True},
            {"refId": "DISK", "expr": f'100 * max by (name) (kubevirt_vmi_filesystem_used_bytes{{namespace="{NS}",mount_point="/"}} / kubevirt_vmi_filesystem_capacity_bytes{{namespace="{NS}",mount_point="/"}})', "format": "table", "instant": True},
            {"refId": "IOPS", "expr": f'sum by (name) (rate(kubevirt_vmi_storage_iops_read_total{{namespace="{NS}"}}[5m]) + rate(kubevirt_vmi_storage_iops_write_total{{namespace="{NS}"}}[5m]))', "format": "table", "instant": True},
            {"refId": "NET", "expr": f'sum by (name) (rate(kubevirt_vmi_network_traffic_bytes_total{{namespace="{NS}"}}[5m]))', "format": "table", "instant": True},
            {"refId": "LAT", "expr": 'label_replace(probe_duration_seconds{job="apache-http"}, "name", "$1", "vm_name", "(.*)")', "format": "table", "instant": True},
            {"refId": "PROBE", "expr": 'label_replace(probe_success{job="apache-http"}, "name", "$1", "vm_name", "(.*)")', "format": "table", "instant": True},
            {"refId": "ALERTS", "expr": 'label_replace(sum by (vm_name) (ALERTS{alertstate="firing", vm_name!=""}), "name", "$1", "vm_name", "(.*)")', "format": "table", "instant": True},
            {"refId": "STATUS", "expr": status_expr(), "format": "table", "instant": True},
        ],
        "transformations": [
            {"id": "seriesToColumns", "options": {"byField": "name"}},
            {
                "id": "organize",
                "options": {
                    "excludeByName": {
                        "Time": True,
                        "Time 1": True, "Time 2": True, "Time 3": True, "Time 4": True,
                        "Time 5": True, "Time 6": True, "Time 7": True, "Time 8": True, "Time 9": True,
                        "__name__": True, "container": True, "endpoint": True, "instance": True,
                        "job": True, "namespace": True, "node": True, "pod": True, "prometheus": True,
                        "service": True, "vm_name": True, "mount_point": True, "disk_name": True,
                        "kubernetes_vmi_label_kubevirt_io_nodeName": True, "Value #VM": True,
                    },
                    "renameByName": {
                        "name": "VM",
                        "Value #CPU": "CPU %",
                        "Value #MEM": "Memory %",
                        "Value #DISK": "Disk %",
                        "Value #IOPS": "IOPS",
                        "Value #NET": "Network",
                        "Value #LAT": "Latency",
                        "Value #PROBE": "Service",
                        "Value #ALERTS": "Active Alerts",
                        "Value #STATUS": "Status",
                    },
                    "indexByName": {
                        "VM": 0, "Status": 1, "CPU %": 2, "Memory %": 3, "Disk %": 4,
                        "IOPS": 5, "Network": 6, "Latency": 7, "Service": 8, "Active Alerts": 9,
                    },
                },
            },
        ],
    }


def node_graph_nodes_expr() -> str:
    specs = [
        ("prometheus", f'up{{namespace="{OBS_NS}", job="prometheus-operated"}}', "Prometheus", ":9090", "chart-line"),
        ("alertmanager", f'up{{namespace="{OBS_NS}", job="alertmanager-operated"}}', "Alertmanager", ":9093", "bell"),
        ("otel-up", f'up{{namespace="{OBS_NS}", job="otel-collector-upstream"}}', "OTel Upstream", ":8090-8093", "share-alt"),
        ("kafka", 'probe_success{job="observability-kafka-tcp"}', "Kafka", ":9092", "database"),
        ("otel-down", f'up{{namespace="{OBS_NS}", job="otel-collector-downstream"}}', "OTel Downstream", "Kafka consume", "exchange"),
        ("loki", f'up{{namespace="{OBS_NS}", job="loki"}}', "Loki", ":3100", "file-alt"),
        ("grafana", f'up{{namespace="{OBS_NS}", job="grafana"}}', "Grafana", ":3000", "monitor"),
        ("eda", 'probe_success{job="observability-eda-http"}', "AAP EDA", "aiops.alertmanager", "bolt"),
    ]
    parts = []
    for node_id, metric, title, subtitle, icon in specs:
        parts.append(
            f'label_replace('
            f'label_replace('
            f'label_replace('
            f'label_replace({metric}, "id", "{node_id}", "", ""), '
            f'"title", "{title}", "", ""), '
            f'"subtitle", "{subtitle}", "", ""), '
            f'"icon", "{icon}", "", "")'
        )
    return " or ".join(parts)


def node_graph_edges_expr() -> str:
    edges = [
        ("e1", "prometheus", "alertmanager", "alerts :9093"),
        ("e2", "alertmanager", "otel-up", "webhook :8090"),
        ("e3", "otel-up", "kafka", "Kafka produce"),
        ("e4", "kafka", "otel-down", "Kafka consume"),
        ("e5", "otel-down", "loki", "OTLP :3100"),
        ("e6", "prometheus", "grafana", "PromQL :9090"),
        ("e7", "loki", "grafana", "LogQL :3100"),
        ("e8", "kafka", "eda", "aiops.alertmanager"),
    ]
    parts = []
    for edge_id, source, target, label in edges:
        parts.append(
            f'label_replace('
            f'label_replace('
            f'label_replace('
            f'label_replace(vector(1), "id", "{edge_id}", "", ""), '
            f'"source", "{source}", "", ""), '
            f'"target", "{target}", "", ""), '
            f'"mainstat", "{label}", "", "")'
        )
    return " or ".join(parts)


def topology_panel(*, grid_y: int) -> dict:
    return {
        "type": "nodeGraph",
        "title": "Observability Suite Topology",
        "description": "Circular nodes show component health; arrows show data flow direction.",
        "id": 3,
        "gridPos": {"h": 18, "w": 24, "x": 0, "y": grid_y},
        "datasource": {"type": "prometheus", "uid": "prometheus"},
        "fieldConfig": {
            "defaults": {
                "thresholds": THRESHOLDS_UP,
                "mappings": [
                    {"type": "value", "options": {"0": {"color": "red", "text": "DOWN", "index": 0}}},
                    {"type": "value", "options": {"1": {"color": "green", "text": "UP", "index": 1}}},
                ],
            },
            "overrides": [],
        },
        "options": {
            "nodes": {
                "mainStatUnit": "none",
                "arcSections": [],
            },
            "edges": {
                "mainStatUnit": "none",
            },
            "layout": "layered",
        },
        "pluginVersion": "11.3.0",
        "targets": [
            {
                "refId": "nodes",
                "expr": node_graph_nodes_expr(),
                "format": "table",
                "instant": True,
            },
            {
                "refId": "edges",
                "expr": node_graph_edges_expr(),
                "format": "table",
                "instant": True,
            },
        ],
        "transformations": [
            {
                "id": "renameByRegex",
                "options": {
                    "regex": "Value #nodes",
                    "renamePattern": "mainstat",
                },
            },
        ],
    }


def topology_status_table(*, grid_y: int, component_count: int) -> dict:
    """Readable table with explicit component health."""
    status_expr = (
        f'label_replace(up{{namespace="{OBS_NS}", job="prometheus-operated"}}, "component", "Prometheus", "", "") '
        f'or label_replace(up{{namespace="{OBS_NS}", job="alertmanager-operated"}}, "component", "Alertmanager", "", "") '
        f'or label_replace(up{{namespace="{OBS_NS}", job="otel-collector-upstream"}}, "component", "OTel Upstream", "", "") '
        f'or label_replace(probe_success{{job="observability-kafka-tcp"}}, "component", "Kafka", "", "") '
        f'or label_replace(up{{namespace="{OBS_NS}", job="otel-collector-downstream"}}, "component", "OTel Downstream", "", "") '
        f'or label_replace(up{{namespace="{OBS_NS}", job="loki"}}, "component", "Loki", "", "") '
        f'or label_replace(up{{namespace="{OBS_NS}", job="grafana"}}, "component", "Grafana", "", "") '
        f'or label_replace(probe_success{{job="observability-eda-http"}}, "component", "AAP EDA", "", "")'
    )
    table_h = max(4, component_count + 1)
    return {
        "type": "table",
        "title": "Component Health",
        "id": 4,
        "gridPos": {"h": table_h, "w": 24, "x": 0, "y": grid_y},
        "datasource": {"type": "prometheus", "uid": "prometheus"},
        "fieldConfig": {
            "defaults": {
                "custom": {"align": "center", "cellOptions": {"type": "auto"}},
            },
            "overrides": [
                {
                    "matcher": {"id": "byName", "options": "Component"},
                    "properties": [
                        {"id": "custom.align", "value": "left"},
                        {"id": "custom.width", "value": 220},
                    ],
                },
                {
                    "matcher": {"id": "byName", "options": "Status"},
                    "properties": [
                        {"id": "mappings", "value": [
                            {"type": "value", "options": {"0": {"color": "red", "text": "DOWN", "index": 0}}},
                            {"type": "value", "options": {"1": {"color": "green", "text": "UP", "index": 1}}},
                        ]},
                        {"id": "custom.cellOptions", "value": {"type": "color-background"}},
                        {"id": "decimals", "value": 0},
                    ],
                },
            ],
        },
        "options": {
            "showHeader": True,
            "cellHeight": "sm",
            "sortBy": [{"displayName": "Component", "desc": False}],
        },
        "pluginVersion": "11.3.0",
        "targets": [
            {"refId": "A", "expr": status_expr, "format": "table", "instant": True},
        ],
        "transformations": [
            {
                "id": "organize",
                "options": {
                    "excludeByName": {
                        "Time": True,
                        "__name__": True,
                        "container": True,
                        "endpoint": True,
                        "instance": True,
                        "job": True,
                        "namespace": True,
                        "pod": True,
                        "service": True,
                        "component": False,
                    },
                    "renameByName": {
                        "component": "Component",
                        "Value": "Status",
                    },
                    "indexByName": {
                        "Component": 0,
                        "Status": 1,
                    },
                },
            },
        ],
    }


def build_dashboard() -> dict:
    vm_row_y = 0
    vm_table_y = vm_row_y + 1
    vm_table_h = max(4, VM_FLEET_SIZE + 2)
    topo_row_y = vm_table_y + vm_table_h
    topo_panel_y = topo_row_y + 1
    topo_panel_h = 18
    health_table_y = topo_panel_y + topo_panel_h
    component_count = 8

    return {
        "annotations": {"list": []},
        "editable": True,
        "fiscalYearStartMonth": 0,
        "graphTooltip": 0,
        "id": None,
        "links": [],
        "panels": [
            {
                "type": "row",
                "title": "Virtual Machines",
                "id": 10,
                "gridPos": {"h": 1, "w": 24, "x": 0, "y": vm_row_y},
                "collapsed": False,
                "panels": [],
            },
            vm_table_panel(grid_y=vm_table_y, grid_h=vm_table_h),
            {
                "type": "row",
                "title": "Observability Suite Topology",
                "id": 20,
                "gridPos": {"h": 1, "w": 24, "x": 0, "y": topo_row_y},
                "collapsed": False,
                "panels": [],
            },
            topology_panel(grid_y=topo_panel_y),
            topology_status_table(grid_y=health_table_y, component_count=component_count),
        ],
        "refresh": "30s",
        "schemaVersion": 39,
        "tags": ["aiops", "vm", "kubevirt", "observability"],
        "templating": {"list": []},
        "time": {"from": "now-1h", "to": "now"},
        "timepicker": {},
        "timezone": "browser",
        "title": "AIOps VM Fleet",
        "uid": "aiops-vm-fleet",
        "version": 2,
    }


def main() -> None:
    output = Path(__file__).with_name("50-dashboard-vm-fleet.yaml")
    dashboard = build_dashboard()
    header = """apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-dashboard-vm-fleet
  namespace: "{{ observability.namespace }}"
  labels:
    app.kubernetes.io/name: grafana
    app.kubernetes.io/part-of: "{{ observability.part_of_label }}"
data:
  vm-fleet.json: |
"""
    body = json.dumps(dashboard, indent=2)
    indented = "\n".join("    " + line for line in body.splitlines())
    output.write_text(header + indented + "\n", encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
