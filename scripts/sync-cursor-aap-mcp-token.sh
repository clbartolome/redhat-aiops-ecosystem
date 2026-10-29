#!/usr/bin/env bash
# Refresh Cursor's AAP MCP OAuth token from the cluster secret (no stdout).
set -euo pipefail
NAMESPACE="${AAP_MCP_NAMESPACE:-aap}"
SECRET="${AAP_MCP_TOKEN_SECRET:-aap-mcp-agent-token}"
CONF="${AAP_MCP_ENV_FILE:-${HOME}/.config/environment.d/aap-mcp.conf}"
CURSOR_ENV="${AAP_MCP_CURSOR_ENV_FILE:-${HOME}/.config/cursor/aap-mcp.env}"
MCP_URL="${AAP_MCP_URL:-https://ansible-mcp-aap.apps.ocp.zaskan.es/mcp/}"
CA_FILE="${NODE_EXTRA_CA_CERTS:-${HOME}/.local/share/ca-certificates/ocp-ingress/openshift-ingress-ca.crt}"

mkdir -p "$(dirname "${CONF}")" "$(dirname "${CURSOR_ENV}")"
TOKEN="$(oc get secret "${SECRET}" -n "${NAMESPACE}" -o jsonpath='{.data.token}' | base64 -d)"
umask 077
printf 'AAP_MCP_TOKEN=%s\n' "${TOKEN}" > "${CONF}"
chmod 600 "${CONF}"
cat > "${CURSOR_ENV}" <<EOF
AAP_MCP_TOKEN=${TOKEN}
AAP_MCP_URL=${MCP_URL}
NODE_EXTRA_CA_CERTS=${CA_FILE}
EOF
chmod 600 "${CURSOR_ENV}"
unset TOKEN

if command -v dbus-update-activation-environment >/dev/null 2>&1; then
  set -a
  # shellcheck source=/dev/null
  source "${CONF}"
  CA_CONF="${HOME}/.config/environment.d/cursor-ocp-ca.conf"
  if [[ -f "${CA_CONF}" ]]; then
    # shellcheck source=/dev/null
    source "${CA_CONF}"
  fi
  set +a
  dbus-update-activation-environment --systemd AAP_MCP_TOKEN NODE_EXTRA_CA_CERTS 2>/dev/null || true
fi

echo "Updated ${CONF} and ${CURSOR_ENV} (used by Cursor MCP envFile)."
echo "Fully quit and reopen Cursor so the aap MCP server reloads."
