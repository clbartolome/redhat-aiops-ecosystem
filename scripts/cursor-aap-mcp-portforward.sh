#!/usr/bin/env bash
# Optional: forward AAP MCP to localhost when you cannot use the route URL.
# Default Cursor config uses https://ansible-mcp-aap.apps.ocp.zaskan.es/mcp/
# after scripts/sync-openshift-ingress-ca.sh installs the ingress CA.
set -euo pipefail
LOCAL_PORT="${AAP_MCP_LOCAL_PORT:-18086}"
REMOTE_PORT="${AAP_MCP_REMOTE_PORT:-8086}"
NAMESPACE="${AAP_MCP_NAMESPACE:-aap}"
SERVICE="${AAP_MCP_SERVICE:-ansible-mcp}"

echo "Forwarding ${NAMESPACE}/svc/${SERVICE} -> 127.0.0.1:${LOCAL_PORT} (remote :${REMOTE_PORT})"
exec oc port-forward -n "${NAMESPACE}" "svc/${SERVICE}" "${LOCAL_PORT}:${REMOTE_PORT}"
