# AAP Configuration-as-Code (CASC)

This component configures Ansible Automation Platform objects for the AIOps demo: organizations, credentials, projects, job templates, workflows, and runtime playbooks.

**Supported workflows:**

| Workflow / JT | Purpose |
|---------------|---------|
| **Deploy Generic Application Stack** | Master workflow: ITSM change → VM → app → expose → complete |
| **Troubleshoot apache application** | Remediate Apache incidents (with **Create Apache Alert Incident**) |
| **Reset** | Tear down demo VMs, ITSM data, and observability probes |

**Event-Driven Ansible (demo observability path):** when `aap_casc.enable_observability_pipelines` is true (default), CASC also configures EDA rulebook activations for Apache Alertmanager alerts and ITSM outbound webhooks to chat, plus AAP log forwarding to the observability stack.

**Scope:** AAP CASC only. ITSM-app and chat-app are installed by [`components/itsm`](../../itsm) and [`components/chat`](../../chat). This component registers AAP credentials for those services and ships runtime playbooks synced to Gitea.

## Prerequisites

- OpenShift cluster with **OpenShift Virtualization** operator installed.
- Ansible Automation Platform 2.7 instance (`AnsibleAutomationPlatform/ansible` in namespace `aap`).
- Ecosystem components installed first: Gitea, ITSM, observability (Kafka), AAP EDA operator.
- Red Hat Automation Hub offline token in `vars.yaml` (`aap_casc.public_ah_token`) or `PUBLIC_AH_OFFLINE_TOKEN` env override.
- `vars.yaml` configured at the repository root (`gitea`, `itsm`, `observability`, `aap_casc`).

## Installation

From the repository root:

```bash
ansible-playbook install.yaml
```

Set `aap_casc.public_ah_token` in `vars.yaml` before install.

The root installer runs `components/aap-casc/deploy/playbooks/casc/install.yml` after Gitea, ITSM, observability, and AAP EDA.

### Standalone CASC install

```bash
cd components/aap-casc/deploy
ansible-playbook playbooks/casc/install.yml \
  -e @../../../vars.yaml \
  -e ocp_host=<your-cluster-domain>
```

## Gitea repositories

| Repository       | Source                          | Consumer              |
|------------------|---------------------------------|-----------------------|
| Playbooks        | `playbooks/casc/playbooks/`     | AAP project SCM       |
| Infrastructure   | `playbooks/casc/infrastructure/`| Argo CD GitOps VMs    |
| AIOps_App        | External Git clone              | Application deploy    |

## Sync playbooks without full install

```bash
cd ansible-navigator
ansible-navigator run ../components/aap-casc/deploy/run-sync-playbooks.yml -m stdout \
  -e "ocp_host=$CLUSTER_DOMAIN" -e "api_token=$OPENSHIFT_TOKEN"
```

## Modular configure playbooks

From `deploy/playbooks/casc/`:

- `sync-playbooks.yml` — push Playbooks to Gitea and sync AAP project SCM
- `configure-aap-credentials.yml` — organization and credentials
- `configure-aap-vm-workflow.yml` — VM stack job templates and inventories
- `configure-aap-httpd-workflow.yml` — Generic Application stack job templates
- `configure-aap-apache-stack-workflow.yml` — master stack workflow
- `configure-aap-apache-troubleshoot-pipeline.yml` — troubleshoot job templates
- `configure-aap-eda-pipeline.yml` — EDA Apache alert rulebook activation
- `configure-aap-eda-itsm-webhook-pipeline.yml` — EDA ITSM webhook → chat activation
- `configure-aap-itsm-chat-pipeline.yml` — Publish ITSM Chat Notification job template
- `configure-aap-reset-pipeline.yml` — Reset job template
- `configure-infrastructure-gitops.yml` — Argo CD for Infrastructure VMs

Re-run `configure-aap-apache-stack-workflow.yml`, VM/httpd configure playbooks, and `sync-playbooks.yml` after workflow or playbook changes.

## Deploy Generic Application Stack

Flat master workflow (no nested sub-workflows):

Resolve ITSM Change → Provision VM Stack → Register ITSM VM Asset → Configure Generic App → (Expose ∥ Register ITSM App) → Complete Generic App Stack.

Consolidated playbooks: `provision_vm.yml`, `configure_generic_app.yml`, `complete_generic_app_stack.yml`. See [`components/itsm/kbs/generic_app_vm.md`](../itsm/kbs/generic_app_vm.md).

Legacy granular playbooks (`push_vm_manifest.yml`, `install_httpd.yml`, etc.) and standalone workflows (`Provision VM`, `Deploy Generic App`) are removed on install.

## Uninstall

```bash
ansible-playbook uninstall.yaml -e @vars.yaml \
  -e "ocp_host=<your-cluster-domain>" \
  -e "api_token=<your-openshift-token>"
```

CASC-only teardown:

```bash
cd ansible-navigator
ansible-navigator run ../components/aap-casc/deploy/run-uninstall.yml -m stdout \
  -e "ocp_host=$CLUSTER_DOMAIN" -e "api_token=$OPENSHIFT_TOKEN"
```

Or from `components/aap-casc/deploy/`:

```bash
ansible-playbook playbooks/casc/uninstall-aap-aiops.yml -e @../../../vars.yaml \
  -e ocp_host=<cluster-domain> -e api_token=<openshift-token>
```

Do not run `components/aap-casc/uninstall.yaml` directly — it is a hook for `import_playbook`, not a standalone playbook.

## Layout

```
components/aap-casc/
├── install.yaml
├── uninstall.yaml
├── README.md
└── deploy/
    ├── group_vars/all/
    ├── roles/
    │   ├── aap-platform-facts/
    │   ├── aap-vm-pipeline/          # VM stack JTs + inventories
    │   ├── aap-httpd-pipeline/       # App stack JTs
    │   ├── aap-apache-stack-pipeline/  # Master workflow
    │   ├── aap-apache-troubleshoot-pipeline/
    │   ├── aap-eda-pipeline/
    │   ├── aap-eda-itsm-webhook-pipeline/
    │   ├── aap-observability-integration/
    │   ├── aap-itsm-chat-pipeline/
    │   ├── aap-reset-pipeline/
    │   └── ...
    └── playbooks/casc/
        ├── install.yml
        └── playbooks/                # Runtime automation (synced to Gitea)
```
