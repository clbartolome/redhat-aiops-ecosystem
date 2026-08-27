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

chat:
  namespace: aiops-tools
  image: quay.io/calopezb/gen-ai-k8s-playground-chat
  ssl_verify: false
  log_level: INFO
  trace_db_path: /tmp/agent-traces.db
  agent_timeout: 120

monitor:
  namespace: aiops-tools
  image: quay.io/calopezb/gen-ai-k8s-playground-monitor
  ssl_verify: false
  log_level: INFO
  trace_db_path: /tmp/agent-traces.db
  agent_timeout: 120
```

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

