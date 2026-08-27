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

TODO EXPLAIN VARS FILE

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

