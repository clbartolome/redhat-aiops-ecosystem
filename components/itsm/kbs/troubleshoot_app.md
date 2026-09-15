# Troubleshoot Apache Application

This article describes the procedure to troubleshoot an apache application.

## Required Information

- vm_name
- itsm_incident_ref

## Procedure

1. Search the job template called "Troubleshoot apache application" in Ansible Automation Platform.

2. Launch the Ansible Automation Platform "Troubleshoot apache application" job template passing the following extra_vars:

    - vm_name: Virtual Machine name
    - itsm_incident_ref: Incident id

## Follow up

Keep ITSM incident ID and relevant launched job ID to follow up the request.