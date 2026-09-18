# Deploy Generic Application Stack

This article describes the procedure to create a Virtual Machine with an application running on it.

## Required Information

- Virtual Machine name
- Virtual Machine number of CPUs
- Virtual Machine memory
- Application Repository

## Procedure

1. Open and **submit** an ITSM service request using the **Generic-Application-Stack** ITSM template providing the following parameters:

    - vm_name: Virtual Machine name
    - cpus: Virtual Machine number of CPUs
    - mem: Amount of memory in GiB
    - app_repo: Git repository in which resides the application code

    Submission creates the linked ITSM change (CHG-*). Do not launch the AAP workflow while the request is still draft.


2. Search the workflow job template called "Deploy Generic Application Stack" in Ansible Automation Platform.


3. Launch the Ansible Automation Platform "Deploy Generic Application Stack" workflow job template passing the following extra_vars:

    - vm_name: Virtual Machine name
    - cpus: Virtual Machine number of CPUs
    - mem: Virtual Machine memory (integer)
    - app_repo: Application Repository
    - itsm_service_request_ref: Obtained in the step 1

## Workflow overview

The optimized master workflow runs six job nodes (expected total time ~2–3 minutes):

1. **Resolve ITSM Change from Request** — resolves `itsm_change_ref` from the service request.
2. **Provision VM Stack** — pushes the VM manifest (including Service and Route) and syncs Argo CD.
3. **Register ITSM VM Asset** — discovers VM IPs and registers the asset in ITSM.
4. **Configure Generic App** — installs packages, deploys the application repository, and starts services on the VM.
5. **Expose application** and **Register ITSM Generic Application Asset** — run in parallel after configure.
6. **Complete Generic App Stack** — final ITSM CTASK aggregation and optional chat notification.

ITSM change-task tracking is limited to milestones: Sync Infrastructure VMs, Expose application, and Start application services (final completion node). Prior CTASKs in the ITSM change template are auto-completed before each milestone so sequential ITSM rules are satisfied. When the final milestone completes, the linked change, RITM, and service request move to completed/fulfilled automatically.

## Follow up

Keep ITSM service request ID and relevant launched job ID to follow up the request. The workflow resolves the linked ITSM change ID automatically.

## Test plan

After deploying CASC changes, validate in AAP:

1. Launch the full workflow and record per-node duration (compare to previous ~5+ minute runs).
2. Confirm ITSM CTASKs are updated only for Sync, Expose, and Start milestones.
3. Confirm SSH to the new VM succeeds without waiting for a full inventory sync.
4. Confirm the OpenShift Route URL is reachable and the chat thread receives the completion summary when launched from the agent.
5. Re-run against an existing VM to verify idempotency.
