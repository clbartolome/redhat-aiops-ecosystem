#!/usr/bin/env bash
# Install OpenShift default ingress CA for local TLS clients (Cursor MCP over routes).
set -euo pipefail
DEST_DIR="${OCP_INGRESS_CA_DIR:-${HOME}/.local/share/ca-certificates/ocp-ingress}"
BUNDLE="${DEST_DIR}/openshift-ingress-router-bundle.pem"
ANCHOR="${DEST_DIR}/openshift-ingress-ca.crt"

mkdir -p "${DEST_DIR}"
oc get secret router-certs-default -n openshift-ingress -o jsonpath='{.data.tls\.crt}' | base64 -d > "${BUNDLE}"

export DEST_DIR
python3 - <<'PY'
from pathlib import Path
import os, ssl
dest = Path(os.environ["DEST_DIR"])
text = (dest / "openshift-ingress-router-bundle.pem").read_text()
chunks = []
buf = ""
for line in text.splitlines(True):
    buf += line
    if "END CERTIFICATE" in line:
        chunks.append(buf)
        buf = ""
if not chunks:
    raise SystemExit("No certificates found in router bundle")
(dest / "openshift-ingress-ca.crt").write_text(chunks[-1])
ssl.create_default_context().load_verify_locations(cafile=str(dest / "openshift-ingress-ca.crt"))
print(f"Updated {dest / 'openshift-ingress-ca.crt'} ({len(chunks)} cert(s) in bundle)")
PY

echo "Restart Cursor so NODE_EXTRA_CA_CERTS is applied."
