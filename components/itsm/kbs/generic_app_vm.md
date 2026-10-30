# Deploy Generic Application Stack

Create a Virtual Machine and deploy an application from a Git repository using the Generic Application Stack workflow.

## Procedure

**ID:** deploy-generic-application-stack
**Version:** 1
**Risk:** medium
**Confirmation required:** yes

## Required information

- **Virtual Machine name** — required — Name of the Virtual Machine to create.
- **Virtual Machine CPUs** — required — Number of CPUs assigned to the Virtual Machine.
- **Virtual Machine memory** — required — Amount of memory assigned to the Virtual Machine in GiB.
- **Application Repository** — required — Git repository containing the application source code.

## Steps

### 1. Create the ITSM service request

Create and submit an ITSM service request using the **Generic-Application-Stack** service request template.

Use the following values:

- `vm_name`: **Virtual Machine name**
- `cpus`: **Virtual Machine CPUs**
- `mem`: **Virtual Machine memory**
- `app_repo`: **Application Repository**

The request must be submitted, not left in draft state.

Keep the created ITSM service request reference because it is required by a later step.

If the service request cannot be created and submitted successfully, fail the procedure and do not continue.

### 2. Launch the deployment workflow

Launch the Ansible Automation Platform workflow job template:

**Deploy Generic Application Stack**

Use the following extra variables:

- `vm_name`: **Virtual Machine name**
- `cpus`: **Virtual Machine CPUs**
- `mem`: **Virtual Machine memory**
- `app_repo`: **Application Repository**
- `itsm_service_request_ref`: the ITSM service request reference created in step 1

Keep the launched workflow job ID so it can be reported to the user and used for follow-up.

If the workflow cannot be launched successfully, fail the procedure.

## Success

The procedure is successful when:

- the ITSM service request has been submitted successfully
- the **Deploy Generic Application Stack** workflow job template has been found
- the workflow has been launched successfully using the requested Virtual Machine and application parameters
- the ITSM service request reference and launched workflow job ID are available for follow-up

## Workflow overview

The deployment workflow performs the following operations:

1. **Resolve ITSM Change from Request** — resolves the ITSM change associated with the service request.
2. **Provision VM Stack** — provisions the Virtual Machine infrastructure and synchronizes it through Argo CD.
3. **Register ITSM VM Asset** — discovers the Virtual Machine network information and registers the asset in ITSM.
4. **Configure Generic App** — installs the required packages, deploys the application repository, and starts the application services.
5. **Expose application** and **Register ITSM Generic Application Asset** — expose the application and register it as an ITSM asset.
6. **Complete Generic App Stack** — completes the final ITSM tasks and associated request records.

## Follow up

Use the ITSM service request reference and the launched Ansible Automation Platform workflow job ID to follow the deployment after this procedure completes.