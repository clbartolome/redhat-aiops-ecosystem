# redhat-aiops-ecosystem

> [!IMPORTANT]  
> Last tested versions (cluster `ocp.zaskan.es`): 
> - OpenShift: **4.21**
> - Ansible Automation Platform operator: **2.7.0+0.1787240540** (`stable-2.7`) — instance `ansible` **2.7.20260824**
> - OpenShift GitOps: **1.21.3** (`latest`)
> - Red Hat OpenShift Streams for Apache Kafka: **3.2.1-10** (`stable`)
> - Prometheus Operator: **0.56.3** (`beta`, namespace `observability`)
> - OpenShift Virtualization: **4.21.16** (`stable`)

## Setup

### Pre-Requisites

#### OpenShift cluster

- OpenShift **4.21** (last tested; see note at top of this file).
- A **default StorageClass** for persistent volumes (Kafka, Loki, Grafana, Gitea Postgres, AAP Postgres, and others).
- Cluster network: **OVN-Kubernetes** with **UserDefinedNetwork** support (required for the VM demo in `aap_casc`; secondary UDN for fixed VM IPs on OCP 4.17+).

#### Operators (install before `install.yaml`)

Install these from **OperatorHub** (or `oc`) on the cluster. None of them are installed by this repository.

| Operator | OLM package name | Catalog | Tested version | Required by |
|----------|------------------|---------|----------------|-------------|
| [Ansible Automation Platform](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/) | `ansible-automation-platform-operator` | Red Hat | **2.7.0+0.1787240540** (`stable-2.7`) | `aap_mcp`, `aap_eda`, `aap_casc` — provides the `AnsibleAutomationPlatform` CR and EDA (`edas.eda.ansible.com`). Deploy an instance named `ansible` in namespace `aap` (or adjust `vars.yaml`). Enable **Event-Driven Ansible** in the operator/AAP install. |
| [OpenShift GitOps](https://docs.openshift.com/gitops/latest/) | `openshift-gitops-operator` | Red Hat | **1.21.3** (`latest`) | `aap_casc` — Argo CD for the Infrastructure GitOps repo (VM manifests). Default instance `openshift-gitops` in `openshift-gitops`. |
| [Red Hat OpenShift Streams for Apache Kafka](https://docs.redhat.com/en/documentation/red_hat_streams_for_apache_kafka/) (Strimzi) | `amq-streams` | Red Hat | **3.2.1-10** (`stable`) | `observability` — `Kafka` / `KafkaTopic` CRs in the observability namespace. |
| [Prometheus Operator](https://github.com/prometheus-operator/prometheus-operator) | `prometheus` | Community (`community-operators`) | **0.56.3** (`beta`) | `observability` — `Prometheus`, `Alertmanager`, `ServiceMonitor`, and `PrometheusRule` CRs. Install with an `OperatorGroup` that targets namespace `observability`. |
| [OpenShift Virtualization](https://docs.openshift.com/virtualization/latest/) | `kubevirt-hyperconverged` | Red Hat | **4.21.16** (`stable`) | `aap_casc` — KubeVirt VMs for provisioning / Apache demo workflows (`aiops-demo` namespace). Only the operator is required; VMs are created by GitOps playbooks. |

Example: verify operators are installed and CRDs are present:

```sh
oc get csv -A | grep -E 'ansible-automation-platform|openshift-gitops|amq-streams|prometheus|kubevirt-hyperconverged'
oc get crd edas.eda.ansible.com ansibleautomationplatforms.aap.ansible.com prometheuses.monitoring.coreos.com 2>/dev/null
oc get ansibleautomationplatform -n aap
```

Prometheus Operator (namespace-scoped example — create the `observability` project first, then apply):

```sh
oc new-project observability --display-name=Observability 2>/dev/null || oc project observability
```

```yaml
# observability namespace must exist before applying the Subscription
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: observability-prometheus
  namespace: observability
spec:
  targetNamespaces:
    - observability
---
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: prometheus
  namespace: observability
spec:
  channel: beta
  name: prometheus
  source: community-operators
  sourceNamespace: openshift-marketplace
  installPlanApproval: Automatic
```

#### Deployed by this repository (not operators)

| Component | How | Notes |
|-----------|-----|--------|
| **OpenShift MCP server** | Helm chart `redhat-openshift-mcp-server` from `https://charts.openshift.io/` | Deployed into `openshift-mcp` namespace during install. |

#### Execution environment

Build the Ansible execution environment:

```sh
cd ansible-navigator
ansible-builder build -t rh-aiops-ee:latest
```

### Configuration

Create a `vars.yaml` file at the repository root. `install.yaml` and `uninstall.yaml` load it automatically.

```sh
cp vars.yaml.example vars.yaml
```

Edit `vars.yaml` and replace every value marked with `<...>`. See `vars.yaml.example` for the full structure and defaults.

`ocp_host` and `api_token` are passed at runtime (`-e`); do not put cluster credentials in `vars.yaml`.

Define components in dependency order (`openshift_mcp` → `aap_mcp` → `aap_eda` → `itsm` → `gitea` → `observability` → `agent` → `chat` / `monitor` → `aap_casc`). Downstream blocks reference the ones above (for example, `agent.openshift_mcp_url` from `openshift_mcp`, `agent.aap_mcp_*` from `aap_mcp`, `agent.itsm_mcp_*` from `itsm`, `chat.agent_url` from `agent`). `gitea.host`, `gitea.root_url`, and `observability.grafana.host` are derived from `ocp_host` passed at runtime.

`aap_casc.public_ah_token` is the Red Hat Automation Hub offline token (from [console.redhat.com](https://console.redhat.com/ansible/automation-hub/token)). You can override it at runtime with `PUBLIC_AH_OFFLINE_TOKEN` without editing `vars.yaml`.

The `aap_eda` component enables Event-Driven Ansible on the existing `AnsibleAutomationPlatform` instance via the operator (`spec.eda.disabled: false`). Set `automation_server_ssl_verify: "no"` for clusters with self-signed certificates.

The observability stack deploys Kafka, OpenTelemetry collectors, Loki, Grafana, Prometheus, and Alertmanager into the `observability` namespace. All monitoring (including Apache HTTP probes in `aiops-demo`) uses the in-namespace Prometheus and Alertmanager from this repo — **OpenShift User Workload Monitoring (UWM) is not used**. Alert flow: **Prometheus → Alertmanager → OTel upstream → Kafka → OTel downstream → Loki**. Grafana is exposed at `observability.grafana.host`. **Strimzi** and the **Prometheus Operator** must already be on the cluster (see operators table above).

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

### Troubleshooting

#### `bitnami/kubectl:1.32` image pull failure (`manifest unknown`)

This repository does **not** reference `bitnami/kubectl`. The tag `1.32` usually comes from another workload on the cluster (often a Helm hook Job or operator cleanup Job) that maps the Kubernetes minor version to a Bitnami image tag. Bitnami removed most versioned tags from `docker.io/bitnami` in 2025, so `bitnami/kubectl:1.32` no longer exists.

**Find the failing workload:**

```sh
oc get pods -A -o json \
  | jq -r '.items[]
    | select(
        ([.status.containerStatuses[]?, .status.initContainerStatuses[]?]
          | any(.state.waiting.message? // "" | test("bitnami/kubectl")))
      )
    | "\(.metadata.namespace)/\(.metadata.name)"'

oc get pods -A -o custom-columns=\
'NS:.metadata.namespace,NAME:.metadata.name,IMAGE:.spec.containers[*].image,INIT:.spec.initContainers[*].image' \
  | grep bitnami/kubectl
```

**Typical sources during this install:**

| When | Likely source |
|------|----------------|
| `Wait for Kafka cluster` in observability | Strimzi entity-operator or broker pods — verify **AMQ Streams** (`amq-streams`) is installed, not an unrelated operator |
| Unrelated namespace | Kyverno, OpenEBS, or other operators ship cleanup Jobs with `bitnami/kubectl` — patch the operator Subscription/CSV or override the image in the operator Helm values |

**Replace the image** (after identifying the Deployment, Job, or Helm release):

- `registry.k8s.io/kubectl:v1.32.9` (matches OpenShift 4.21 / Kubernetes 1.32), or
- `docker.io/bitnamilegacy/kubectl:1.32.4-debian-12-r0` (Bitnami legacy catalog)

**Verify AMQ Streams for observability Kafka:**

```sh
oc get csv -A | grep amq-streams
oc get kafka,pods -n observability
oc describe pod -n observability -l strimzi.io/kind=Kafka
```

Kafka manifests in this repo use Strimzi CRs with Red Hat AMQ Streams; broker and entity-operator images should come from `registry.redhat.io/amq-streams/`, not Bitnami.

