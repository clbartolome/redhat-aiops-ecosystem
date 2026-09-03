"""Sync admin and aiops user passwords from environment variables."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, "/app")

from app.services import users_admin as usr_svc


def main() -> None:
    admin_user = os.environ.get("ITSM_SYNC_ADMIN_USER", "").strip() or os.environ.get(
        "ITSM_BOOTSTRAP_ADMIN_USER", ""
    ).strip()
    admin_password = os.environ.get("ITSM_SYNC_ADMIN_PASSWORD") or os.environ.get(
        "ITSM_BOOTSTRAP_ADMIN_PASSWORD", ""
    )
    aiops_password = os.environ.get("ITSM_SYNC_AIOPS_PASSWORD") or os.environ.get(
        "ITSM_SEED_AIOPS_PASSWORD", ""
    )
    targets = {
        admin_user: admin_password,
        "aiops": aiops_password,
    }
    for user in usr_svc.list_users():
        password = targets.get(user["username"])
        if password:
            usr_svc.update_user(user["id"], password=password)
            print(f"updated {user['username']}")


if __name__ == "__main__":
    main()
