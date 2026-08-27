# Deploy Generic Application Stack

This article describes the procedure to create a Virtual Machine with an application running on it.

## Required Information

- Virtual Machine name
- Virtual Machine number of CPUs
- Virtual Machine memory
- Application Repository

## Procedure

1. Open an ITSM service request using the **Generic-Application-Stack** template providing the following values:

    - vm_name: Virtual Machine name
    - cpus: Virtual Machine number of CPUs
    - mem: Amount of memory in GiB
    - app_repo: Git repository in which resides the application code


2. Search the workflow job template called **Deploy Generic Application Stack** in Ansible Automation Platform.


3. Launch the AAP workflow job template passing the following parameters:

    - vm_name: Virtual Machine name
    - cpus: Virtual Machine number of CPUs
    - mem: Virtual Machine memory (integer)
    - app_repo: Application Repository
    - itsm_change_ref: Obtained in the step 1
    - itsm_service_request_ref: Obtained in the step 1

## Follow up

Keep ITSM service request ID, change ID and relevant launched job ID to follow up the request.