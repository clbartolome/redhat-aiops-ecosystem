#!/usr/bin/env python3
"""Update AAP pipeline role preflights to use aap_platform facts."""
from pathlib import Path
import re

ROLES_DIR = Path("/home/rafsanch/Projects/redhat-aiops-ecosystem/components/aap-casc/deploy/roles")

ROLE_PREFIX = {
    "aap-casc": "aap_casc",
    "aap-vm-pipeline": "aap_vm_pipeline",
    "aap-vm-modification-pipeline": "aap_vm_modification_pipeline",
    "aap-httpd-pipeline": "aap_httpd_pipeline",
    "aap-apache-stack-pipeline": "aap_apache_stack_pipeline",
    "aap-apache-troubleshoot-pipeline": "aap_apache_troubleshoot_pipeline",
    "aap-lightspeed-remediation-pipeline": "aap_lightspeed_remediation_pipeline",
    "aap-reset-pipeline": "aap_reset_pipeline",
    "aap-itsm-chat-pipeline": "aap_itsm_chat_pipeline",
    "aap-uninstall": "aap_uninstall",
    "aap-eda-pipeline": "aap_eda_pipeline",
    "aap-eda-itsm-webhook-pipeline": "aap_eda_itsm_webhook_pipeline",
}


def jinja(expr: str) -> str:
    return '"{{ ' + expr + ' }}"'


def jinja_path(host_var: str, path: str) -> str:
    return '"{{ ' + host_var + ' }}' + path + '"'


def build_preflight(role_name: str, prefix: str) -> str:
    lines = [
        "---",
        "- name: Fail when platform facts are not loaded",
        "  ansible.builtin.fail:",
        "    msg: Run aap-platform-facts before this pipeline.",
        "  when: aap_platform is not defined",
        "",
        "- name: Set AAP controller connection facts from platform facts",
        "  ansible.builtin.set_fact:",
        f"    {prefix}_controller_host: " + jinja("aap_platform.aap.gateway_url"),
        f"    {prefix}_controller_username: " + jinja("aap_platform.aap.username"),
        f"    {prefix}_controller_password: " + jinja("aap_platform.aap.password"),
    ]
    if role_name == "aap-casc":
        lines.append(
            f"    {prefix}_openshift_namespace: " + jinja("aap_platform.aap.namespace")
        )
        lines.append(
            f"    {prefix}_ah_offline_token: " + jinja("aap_platform_ah_offline_token")
        )
    if role_name in ("aap-eda-pipeline", "aap-vm-pipeline"):
        lines.extend([
            f"    {prefix}_gitea_scm_url: >-",
            "      {{",
            f"        ('http://' ~ {prefix}_gitea_scm_internal_host ~ '/'",
            f"         ~ aap_platform.gitea.username ~ '/' ~ {prefix}_gitea_repo ~ '.git')",
            f"        if ({prefix}_gitea_scm_use_internal | default(true) | bool)",
            "        else (",
            "          aap_platform.gitea.url",
            "          | replace('.apps.apps.', '.apps.')",
            "          | regex_replace('/$', '')",
            f"          ~ '/' ~ aap_platform.gitea.username ~ '/' ~ {prefix}_gitea_repo ~ '.git'",
            "        )",
            "      }}",
        ])
    if role_name == "aap-eda-pipeline":
        lines.insert(
            lines.index(f"    {prefix}_controller_password: " + jinja("aap_platform.aap.password")) + 1,
            f"    {prefix}_eda_url: "
            + jinja("aap_platform.aap.eda_url | default(aap_platform.aap.gateway_url)"),
        )
    lines.extend(["  no_log: true", ""])
    if role_name == "aap-casc":
        lines.extend([
            "- name: Fail when VM SSH private key is missing from platform facts",
            "  ansible.builtin.fail:",
            "    msg: >-",
            "      aap_platform.virtualization.ssh_privatekey is missing. Re-run aiops-demo-prep",
            "      to populate VM SSH keys.",
            "  when: aap_platform.virtualization.ssh_privatekey | default('') | trim | length == 0",
            "",
        ])
    if role_name.startswith("aap-eda"):
        lines.extend([
            "- name: Probe EDA API via AAP gateway",
            "  ansible.builtin.uri:",
            f"    url: {jinja_path(prefix + '_controller_host', '/api/eda/v1/decision-environments/')}",
            f"    user: {jinja(prefix + '_controller_username')}",
            f"    password: {jinja(prefix + '_controller_password')}",
            "    method: GET",
            f"    validate_certs: {jinja(prefix + '_validate_certs')}",
            "    force_basic_auth: true",
            "    status_code: 200",
            f"  register: {prefix}_eda_probe",
            "  no_log: true",
            "",
            "- name: Fail when EDA API is not reachable via AAP gateway",
            "  ansible.builtin.fail:",
            "    msg: >-",
            f"      EDA API probe failed at {jinja_path(prefix + '_controller_host', '/api/eda/v1/')}.",
            "      Confirm Event-Driven Ansible is installed.",
            f"  when: {prefix}_eda_probe.status | default(0) != 200",
            "",
            "- name: Normalize EDA URL to gateway when integrated with AAP 2.7",
            "  ansible.builtin.set_fact:",
            f"    {prefix}_eda_url: {jinja(prefix + '_controller_host')}",
            "",
        ])
    else:
        lines.extend([
            "- name: Verify AAP Controller API responds",
            "  ansible.builtin.uri:",
            f"    url: {jinja_path(prefix + '_controller_host', '/api/controller/v2/ping/')}",
            "    method: GET",
            f"    user: {jinja(prefix + '_controller_username')}",
            f"    password: {jinja(prefix + '_controller_password')}",
            "    force_basic_auth: true",
            f"    validate_certs: {jinja(prefix + '_validate_certs')}",
            "    status_code: 200",
            "  no_log: true",
            "",
        ])
    return "\n".join(lines) + "\n"


for role_name, prefix in ROLE_PREFIX.items():
    role_path = ROLES_DIR / role_name
    if not role_path.exists():
        continue
    (role_path / "tasks" / "preflight.yml").write_text(build_preflight(role_name, prefix))
    print(f"updated {role_name}")
