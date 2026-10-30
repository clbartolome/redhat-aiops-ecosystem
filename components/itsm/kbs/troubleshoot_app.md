# Troubleshoot Apache Application

Troubleshoot an Apache application running on a Virtual Machine by launching the corresponding Ansible Automation Platform job.

## Procedure

**ID:** troubleshoot-apache-application
**Version:** 1
**Risk:** low
**Confirmation required:** yes

## Required information

- **Virtual Machine name** — required — Name of the Virtual Machine hosting the Apache application.
- **ITSM incident reference** — required — ITSM incident identifier associated with the troubleshooting request.

## Steps

### 1. Find the troubleshooting job template

Find the Ansible Automation Platform job template named **Troubleshoot apache application**.

Confirm that the job template exists and can be launched.

If the job template cannot be found, fail the procedure and do not continue.

### 2. Launch the troubleshooting job

Launch the Ansible Automation Platform job template **Troubleshoot apache application** with the following values:

- `vm_name`: **Virtual Machine name**
- `itsm_incident_ref`: **ITSM incident reference**

Keep the launched job ID for follow-up.

If the job cannot be launched successfully, fail the procedure.

## Success

The procedure is successful when:

- the **Troubleshoot apache application** job template is found
- the job is launched successfully
- the ITSM incident reference is passed to the job
- the launched job ID is available for follow-up

## Follow up

Keep:

- the ITSM incident reference
- the launched Ansible Automation Platform job ID

Use both identifiers to follow the troubleshooting request.