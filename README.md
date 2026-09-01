# redhat-aiops-ecosystem

> [!IMPORTANT]  

> - OpenShift: **4.21**


## Setup

### Pre-Requisites

The following operators must be installed in the cluster

> - Ansible Automation Platform operator: **2.7.0+0.1787240540** (`stable-2.7`) — instance `ansible` **2.7.20260824**
> - OpenShift GitOps: **1.21.3** (`latest`)
> - Red Hat OpenShift Streams for Apache Kafka: **3.2.1-10** (`stable`)
> - Prometheus Operator: **0.56.3** (`beta`, namespace `observability`)
> - OpenShift Virtualization: **4.21.16** (`stable`)

Build the Ansible execution environment:

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

Define components in dependency order (`openshift_mcp` → `aap_mcp` → `aap_eda` → `itsm` → `gitea` → `observability` → `agent` → `chat` / `monitor` → `aap_casc`). Downstream blocks reference the ones above (for example, `agent.openshift_mcp_url` from `openshift_mcp`, `agent.aap_mcp_*` from `aap_mcp`, `agent.itsm_mcp_*` from `itsm`, `chat.agent_url` from `agent`). `gitea.host`, `gitea.root_url`, and `observability.grafana.host` are derived from `ocp_host` passed at runtime.

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

