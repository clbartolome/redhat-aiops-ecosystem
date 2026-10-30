# redhat-aiops-ecosystem

> [!IMPORTANT]  
> This demo uses a custom agent developed for this demo named **aiops-agent**. [Here](https://github.com/clbartolome/aiops-agent) is the source repository.

## Setup

### Pre-Requisites

The following operators must be installed in the cluster

> - Ansible Automation Platform operator: **2.7.0+0.1787240540** (`stable-2.7`) — instance `ansible` **2.7.20260824**
> - OpenShift GitOps: **1.21.3** (`latest`)
> - Red Hat OpenShift Streams for Apache Kafka: **3.2.1-10** (`stable`)
> - Cluster Observability Operator: **latest** (`stable`, All namespaces)
> - OpenShift Virtualization: **4.21.16** (`stable`)

Build the Ansible execution environment:cd an

```sh
cd ansible-navigator
ansible-builder build -t rh-aiops-ee:latest
```



### Configuration

```sh
cp vars.yaml.example vars.yaml
```

Edit `vars.yaml` and replace every value marked with `<...>`. See `vars.yaml.example` for the full structure and defaults.

`ocp_host` and `api_token` are passed at runtime (`-e`); do not put cluster credentials in `vars.yaml`.

Define components in dependency order (`openshift_mcp` → `aap_mcp` → `aap_eda` → `itsm` → `gitea` → `observability` → `agent` → `aap_casc`). Downstream blocks reference the ones above (for example, `agent.openshift_mcp_url` from `openshift_mcp`, `agent.aap_mcp_*` from `aap_mcp`, `agent.itsm_mcp_*` from `itsm`, `agent.incidents_url` for EDA → agent notifications). `gitea.host`, `gitea.root_url`, and `observability.grafana.host` are derived from `ocp_host` passed at runtime.

`aap_casc.public_ah_token` is the Red Hat Automation Hub offline token (from [console.redhat.com](https://console.redhat.com/ansible/automation-hub/token)).

### Install

- Open a terminal
- Login into OpenShift
- Access installation->ansible-navigator: `cd ansible-navigator`
- Configure openshift environment:

```sh
export OPENSHIFT_TOKEN=$(oc whoami --show-token)
export CLUSTER_DOMAIN=$(oc whoami --show-server | sed 's~https://api\.~~' | sed 's~:.*~~')
```

- Run installation:

```sh
ansible-navigator run ../install.yaml -m stdout \
    -e "ocp_host=$CLUSTER_DOMAIN" \
    -e "api_token=$OPENSHIFT_TOKEN"
```



### Troubleshooting agent and MCP

**OpenShift MCP URL path:** The Helm `kubernetes-mcp-server` endpoint is `http://openshift-mcp-server.<namespace>.svc.cluster.local:8080/mcp` with **no** trailing slash. A URL ending in `/mcp/` returns HTTP 404 from that server. AAP MCP and ITSM still use a trailing `/mcp/` where their servers expect it.

**Empty `OPENSHIFT_MCP_TOKEN` is normal in-cluster:** The OpenShift MCP pod uses its ServiceAccount (RBAC `view`) for the Kubernetes API. The agent only needs a bearer token when calling MCP over a Route with OAuth passthrough.

**If chat fails before any MCP tool runs:** Check agent logs for `OperationalError: near "RETURNING": syntax error`. The [aiops-agent](https://github.com/clbartolome/aiops-agent) uses `openai-agents` `SQLiteSession`, which requires **SQLite 3.35+** in the container Python (`sqlite3.sqlite_version`). The published `quay.io/calopezb/aiops-agent:1.0` image currently ships SQLite 3.34.1 on UBI, so chat sessions fail and logs show `MCP calls attempted=0`. Rebuild the agent image from a base with SQLite ≥ 3.35 (for example `python:3.12-bookworm`) and set `agent.image` in `vars.yaml`, or wait for an updated image tag.

Quick checks from a running agent pod:

```sh
oc exec -n aiops-tools deploy/agent -- python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
oc logs -n aiops-tools deploy/agent | grep 'MCP server='
oc logs -n aiops-tools deploy/agent | grep -E 'RETURNING|mcp_attempted'
```

### Clean-up

Uninstall removes the demo workloads (AAP CASC, ITSM, observability, agent, and so on) but **keeps** Event-Driven Ansible, AAP MCP, and OpenShift MCP. Re-running install skips those components when they are already running; `install.yml` CASC configure still ensures EDA decision environments, projects, and activations exist.

- Open a terminal
- Login into OpenShift
- Access installation->ansible-navigator: `cd ansible-navigator`
- Configure openshift environment:

```sh
export OPENSHIFT_TOKEN=$(oc whoami --show-token)
export CLUSTER_DOMAIN=$(oc whoami --show-server | sed 's~https://api\.~~' | sed 's~:.*~~')
```

- Run cleanup:

```sh
ansible-navigator run ../uninstall.yaml -m stdout \
    -e "ocp_host=$CLUSTER_DOMAIN" \
    -e "api_token=$OPENSHIFT_TOKEN"
```

