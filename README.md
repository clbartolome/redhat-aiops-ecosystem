# redhat-aiops-ecosystem

> [!IMPORTANT]  
> Last tested versions: 
> - OpenShift: 4.21
> - TODO

## Setup

### Pre-Requisites

- Install **OpenShift GitOps** operator (default config)

- TODO operators

- Build execution environment

```sh
cd ansible-navigator
ansible-builder build -t rh-aiops-ee:latest
```

### Configuration

Create a `vars.yaml` file at the repository root. `install.yaml` and `uninstall.yaml` load it automatically. Copy the template below and replace the values marked with `<...>`.

`ocp_host` and `api_token` are passed at runtime (`-e`); do not put cluster credentials in this file.

```yaml
---
kubeconfig:
  ocp_domain: "{{ ocp_host }}"
  ocp_api_token: "{{ api_token }}"

openshift_mcp:
  namespace: openshift-mcp

itsm:
  namespace: itsm-app
  image: image-registry.openshift-image-registry.svc:5000/itsm-app/itsm-app:latest
  session_secret: <replace-with-long-random-string>
  mcp_token: <your-itsm-mcp-token>
  bootstrap_admin_user: admin
  bootstrap_admin_password: <your-bootstrap-admin-password>
  seed_aiops_password: <your-seed-aiops-password>
  embedding_base_url: <embedding-url>
  embedding_model: <embedding-model>
  embedding_api_key: <embedding-pass>
  kb_repo_url: https://github.com/clbartolome/redhat-aiops-ecosystem
  kb_repo_path: components/itsm/kbs

agent:
  namespace: aiops-tools
  image: quay.io/calopezb/gen-ai-k8s-playground-agent
  llm_url: <your-llm-url>
  llm_api_key: <your-llm-api-key>
  llm_model: <your-llm-model>
  llm_timeout: 150
  tools_timeout: 60
  ssl_verify: false
  log_level: INFO
  trace_db_path: /tmp/agent-traces.db
  openshift_mcp_url: http://openshift-mcp-server.{{ openshift_mcp.namespace }}.svc:8080/mcp/
  itsm_mcp_url: http://itsm-app.{{ itsm.namespace }}.svc:8000/mcp/
  itsm_mcp_token: "{{ itsm.mcp_token }}"

chat:
  namespace: "{{ agent.namespace }}"
  image: quay.io/calopezb/gen-ai-k8s-playground-chat
  ssl_verify: false
  log_level: INFO
  trace_db_path: /tmp/agent-traces.db
  agent_url: http://agent.{{ agent.namespace }}.svc:8080
  agent_timeout: 120

monitor:
  namespace: "{{ agent.namespace }}"
  image: quay.io/calopezb/gen-ai-k8s-playground-monitor
  ssl_verify: false
  log_level: INFO
  trace_db_path: /tmp/agent-traces.db
  agent_url: http://agent.{{ agent.namespace }}.svc:8080
  agent_timeout: 120
```

Define components in dependency order (`openshift_mcp` → `itsm` → `agent` → `chat` / `monitor`). Downstream blocks reference the ones above (for example, `agent.openshift_mcp_url` from `openshift_mcp`, `agent.itsm_mcp_*` from `itsm`, `chat.agent_url` from `agent`).

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

### Clean-up

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

