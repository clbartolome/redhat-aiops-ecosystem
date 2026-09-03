"""Apply SESSION_MAX_AGE_SECONDS to Starlette SessionMiddleware when configured."""

from __future__ import annotations

import os
import pathlib

_MAIN = pathlib.Path("/app/app/main.py")
_OLD = (
    'app.add_middleware(SessionMiddleware, secret_key=_session_secret, '
    'session_cookie="itsm_session")'
)
_NEW = (
    'app.add_middleware(SessionMiddleware, secret_key=_session_secret, '
    'session_cookie="itsm_session", '
    'max_age=int(os.environ.get("SESSION_MAX_AGE_SECONDS", "1209600")))'
)


def main() -> None:
    max_age = os.environ.get("SESSION_MAX_AGE_SECONDS", "").strip()
    if not max_age:
        return
    text = _MAIN.read_text()
    if _OLD in text and _NEW not in text:
        _MAIN.write_text(text.replace(_OLD, _NEW))


if __name__ == "__main__":
    main()
