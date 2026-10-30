# Inspect Virtual Machine Deployment

Inspect an OpenShift Virtual Machine and correlate its current runtime, networking, ITSM service request, and Ansible Automation Platform deployment workflow.

## Procedure

**ID:** inspect-virtual-machine-deployment
**Version:** 1
**Risk:** low
**Confirmation required:** no

## Required information

- **Namespace** — required — OpenShift namespace where the Virtual Machine is expected to exist.
- **Virtual Machine name** — required — Name of the Virtual Machine to inspect.

## Steps

### 1. Verify that the namespace exists

Check that **Namespace** exists in the OpenShift cluster.

If the namespace does not exist, stop the procedure and inform the user.

### 2. Find the Virtual Machine

Find the Virtual Machine named **Virtual Machine name** in **Namespace**.

Retrieve its current Virtual Machine configuration and determine whether the Virtual Machine exists.

If the Virtual Machine does not exist, stop the procedure and inform the user.

Keep any relevant identifiers, labels, annotations, and metadata because they may be useful for correlating the Virtual Machine with other resources.

### 3. Inspect the Virtual Machine runtime state

Inspect the current runtime state of **Virtual Machine name** in **Namespace**.

Determine, when available:

- whether the Virtual Machine is running or stopped
- the current Virtual Machine instance state
- the node where it is running
- internal IP addresses
- network interfaces
- relevant runtime conditions

Report unavailable information explicitly rather than guessing.

### 4. Inspect Virtual Machine networking

Inspect the networking resources associated with **Virtual Machine name** in **Namespace**.

Determine, when available:

- Services associated with the Virtual Machine
- exposed ports
- target ports
- protocol
- Service IP addresses
- external or load balancer addresses
- Routes associated with the Virtual Machine or its application
- Route hostnames and URLs

Use resource names, labels, selectors, owner references, and other available metadata to correlate networking resources with the Virtual Machine.

If no Route exists, report that explicitly and continue the procedure.

If no Service exists, report that explicitly and continue the procedure.

### 5. Find the ITSM service request that created the Virtual Machine

Search the available ITSM service requests for the request associated with **Virtual Machine name**.

Use the Virtual Machine name and any identifiers, labels, annotations, or references discovered in previous steps to correlate the Virtual Machine with its originating request.

When the matching request is found, retrieve its details.

Report, when available:

- service request reference
- request status
- request template
- requested Virtual Machine name
- requested CPU count
- requested memory
- requested application repository
- creation and completion information
- comments or notes included in the request details

Keep the service request reference because it may be useful for identifying the deployment workflow.

If no matching service request can be identified confidently, report that the originating ITSM request could not be determined and continue the procedure.

Do not guess a request based only on weak similarity.

### 6. Identify the Ansible Automation Platform deployment workflow

Find the Ansible Automation Platform workflow execution that most likely created **Virtual Machine name**.

Use available correlation information from previous steps, including when available:

- Virtual Machine name
- ITSM service request reference
- request metadata
- workflow execution inputs
- workflow job details

Prefer a workflow execution associated with the **Deploy Generic Application Stack** workflow when the available evidence indicates that procedure was used.

Retrieve the workflow job details and report, when available:

- workflow job ID
- workflow job name
- workflow status
- start time
- finish time
- associated workflow job template
- relevant execution inputs or extra variables
- associated ITSM service request reference

If no matching workflow execution can be identified confidently, report that the deployment workflow could not be determined and continue.

Do not guess a workflow execution.

### 7. Correlate the deployment information

Review the information collected from OpenShift, ITSM, and Ansible Automation Platform.

Provide a concise correlation of:

- Virtual Machine identity
- current Virtual Machine state
- IP addresses
- exposed ports
- Route or external URL when available
- originating ITSM service request when identified
- service request status and comments when available
- AAP workflow execution when identified
- workflow execution status

Highlight any missing or inconsistent correlation.

Examples include:

- the Virtual Machine exists but no originating ITSM request can be identified
- the ITSM request exists but no corresponding AAP workflow can be found
- the workflow completed successfully but the Virtual Machine is not currently running
- a Service exists but no Route exposes it externally

Do not perform remediation.

## Success

The procedure is successful when:

- the namespace exists
- the requested Virtual Machine exists
- its current runtime state has been inspected
- its available network information has been inspected
- an attempt has been made to correlate the Virtual Machine with its originating ITSM service request
- an attempt has been made to correlate the deployment with its Ansible Automation Platform workflow

The absence of an ITSM request, workflow execution, Service, or Route does not by itself fail the procedure when the available systems do not contain enough information to establish that relationship.

Any unavailable or unverified information must be reported explicitly rather than inferred.