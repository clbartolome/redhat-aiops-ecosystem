"""List or create the ITSM outbound webhook for the observability pipeline."""

from __future__ import annotations

import base64
import json
import os
import sys
import urllib.error
import urllib.request


def _auth_header() -> dict[str, str]:
    user = os.environ.get("ITSM_SYNC_ADMIN_USER", "").strip() or os.environ.get(
        "ITSM_BOOTSTRAP_ADMIN_USER", ""
    ).strip()
    password = os.environ.get("ITSM_SYNC_ADMIN_PASSWORD") or os.environ.get(
        "ITSM_BOOTSTRAP_ADMIN_PASSWORD", ""
    )
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def list_webhooks() -> None:
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/v1/settings/webhooks",
        headers=_auth_header(),
    )
    print(urllib.request.urlopen(req).read().decode())


def ensure_webhook() -> None:
    url = os.environ["ITSM_OBSERVABILITY_WEBHOOK_URL"]
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/v1/settings/webhooks",
        headers=_auth_header(),
    )
    existing = json.loads(urllib.request.urlopen(req).read().decode())
    if any(item.get("url") == url for item in existing):
        print("webhook already configured")
        return

    body = json.dumps(
        {"url": url, "label": "AIOps observability", "enabled": True}
    ).encode()
    create = urllib.request.Request(
        "http://127.0.0.1:8000/api/v1/settings/webhooks",
        data=body,
        method="POST",
        headers={**_auth_header(), "Content-Type": "application/json"},
    )
    print(urllib.request.urlopen(create).read().decode())


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in {"list", "ensure"}:
        raise SystemExit("usage: observability_webhook.py <list|ensure>")
    try:
        if sys.argv[1] == "list":
            list_webhooks()
        else:
            ensure_webhook()
    except urllib.error.HTTPError as exc:
        raise SystemExit(exc.read().decode() or str(exc)) from exc


if __name__ == "__main__":
    main()
