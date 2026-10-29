#!/usr/bin/env bash
# Write OpenShift API token for Cursor console MCP (no token on stdout).
set -euo pipefail
CURSOR_ENV="${OPENSHIFT_MCP_CURSOR_ENV_FILE:-${HOME}/.config/cursor/openshift-mcp.env}"
MCP_URL="${OPENSHIFT_MCP_URL:-https://console-openshift-console.apps.ocp.zaskan.es/mcp}"
CA_FILE="${NODE_EXTRA_CA_CERTS:-${HOME}/.local/share/ca-certificates/ocp-ingress/openshift-ingress-ca.crt}"

mkdir -p "$(dirname "${CURSOR_ENV}")"
TOKEN="$(oc whoami -t)"
umask 077
cat > "${CURSOR_ENV}" <<EOF
OPENSHIFT_TOKEN=${TOKEN}
NODE_EXTRA_CA_CERTS=${CA_FILE}
EOF
chmod 600 "${CURSOR_ENV}"
unset TOKEN

echo "Updated ${CURSOR_ENV} (console MCP at ${MCP_URL})."
echo "Fully quit and reopen Cursor so the openshift MCP server reloads."
