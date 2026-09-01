# AAP Configuration-as-Code (CASC)

This component configures Ansible Automation Platform and Event-Driven Ansible objects for the AIOps demo: organizations, credentials, projects, job templates, workflows, and EDA rulebook activations.

**Scope:** AAP/EDA CASC only. ITSM-app and chat-app are installed and configured by [`components/itsm`](../../itsm) and [`components/chat`](../../chat). This component registers AAP credentials for those services and ships runtime playbooks that call them during job execution.

## Prerequisites

- OpenShift cluster with **OpenShift Virtualization** operator installed (only the operator is required on the cluster; this component prepares the `aiops-demo` namespace, SSH keys, and UDN).
- Ansible Automation Platform 2.7 instance (`AnsibleAutomationPlatform/ansible` in namespace `aap`).
- Ecosystem components installed first: Gitea, ITSM, observability (Kafka), AAP EDA operator.
- Red Hat Automation Hub offline token in `vars.yaml` (`aap_casc.public_ah_token`) or `PUBLIC_AH_OFFLINE_TOKEN` env override.
- `vars.yaml` configured at the repository root (`gitea`, `itsm`, `observability`, `aap_casc`).

## Installation

From the repository root:

```bash
ansible-playbook install.yaml
```

Set `aap_casc.public_ah_token` in `vars.yaml` before install. Optionally export `PUBLIC_AH_OFFLINE_TOKEN` to override without editing the file.

The root installer runs `components/aap-casc/deploy/playbooks/casc/install.yml` after Gitea, ITSM, observability, and AAP EDA.

### Standalone CASC install

```bash
cd components/aap-casc/deploy
ansible-playbook playbooks/casc/install.yml \
  -e @../../../vars.yaml \
  -e ocp_host=<your-cluster-domain>
```

## Gitea repositories

Before AAP projects sync, the following repositories are created and populated in Gitea:

| Repository       | Source                          | Consumer              |
|------------------|---------------------------------|-----------------------|
| Playbooks        | `playbooks/casc/playbooks/`     | AAP project SCM       |
| Rulebooks        | `playbooks/casc/rulebooks/`     | EDA project SCM       |
| Infrastructure   | `playbooks/casc/infrastructure/`| Argo CD GitOps VMs    |
| AIOps_App        | External Git clone              | Apache deployment JT  |

## Sync playbooks without full install

Push local runtime playbooks to Gitea and refresh the **AIOps Playbooks** AAP project.
Gitea admin credentials are read from OpenShift (`gitea-secret` and `gitea-host-config` in the Gitea namespace). AAP gateway credentials come from the `AnsibleAutomationPlatform` CR and its admin password secret.

From `components/aap-casc/deploy` (requires `oc login` and Ansible collections from `collections/requirements.yml`):

```bash
ansible-galaxy collection install -r collections/requirements.yml
ansible-playbook playbooks/casc/sync-playbooks.yml
```

With the execution environment from the repo root:

```bash
cd ansible-navigator
ansible-navigator run ../components/aap-casc/deploy/playbooks/casc/sync-playbooks.yml -m stdout
```

Optional: limit which Gitea repos are synced (default is **Playbooks** only):

```bash
ansible-playbook playbooks/casc/sync-playbooks.yml \
  -e '{"gitea_repos_sync_only": ["Playbooks", "Rulebooks"]}'
```

## Modular configure playbooks

Re-run individual pipelines from `deploy/playbooks/casc/`:

- `sync-playbooks.yml` — push Playbooks to Gitea and sync AAP project SCM
- `configure-aap-credentials.yml` — organization and credentials
- `configure-aap-vm-workflow.yml` — VM provisioning workflow
- `configure-aap-httpd-workflow.yml` — Apache application workflow
- `configure-aap-apache-stack-workflow.yml` — master stack workflow
- `configure-aap-eda-pipeline.yml` — EDA Apache alert activation
- `configure-aap-reset-pipeline.yml` — Reset job template

## Uninstall

From the repository root (recommended — includes all components):

```bash
ansible-playbook uninstall.yaml -e @vars.yaml \
  -e "ocp_host=<your-cluster-domain>" \
  -e "api_token=<your-openshift-token>"
```

CASC-only teardown from `deploy/`:

```bash
ansible-playbook playbooks/casc/uninstall-aap-aiops.yml -e @../../../vars.yaml
```

## Layout

```
components/aap-casc/
├── install.yaml              # hook for root installer
├── uninstall.yaml
├── README.md
└── deploy/
    ├── ansible.cfg
    ├── collections/requirements.yml
    ├── group_vars/all/       # pipeline names, ITSM contracts, surveys
    ├── roles/
    │   ├── aap-platform-facts/   # discover AAP, Gitea, ITSM, Kafka URLs
    │   ├── aap-controller/       # shared Gateway OAuth authentication
    │   ├── aiops-demo-prep/      # VM namespace, SSH keys, UDN
    │   ├── aap-casc/             # org, credential types, credentials
    │   ├── aap-*-pipeline/       # per-pipeline CASC roles
    │   └── gitea-repos/          # Gitea repo sync
    └── playbooks/casc/
        ├── install.yml           # full orchestration
        ├── playbooks/            # runtime automation (synced to Gitea)
        ├── rulebooks/            # EDA rulebooks (synced to Gitea)
        └── infrastructure/       # GitOps VM manifests
```
