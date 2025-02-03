#!/usr/bin/python3
from __future__ import annotations

import platform
from pathlib import Path


def getpy(pyfile: str | None) -> str | None:
    if not pyfile:
        return None

    pypath = Path(pyfile)
    if not pypath.is_dir():
        return pyfile

    binpath = 'Scripts' if platform.system() == 'Windows' else 'bin'
    return str(pypath / binpath / 'python')
