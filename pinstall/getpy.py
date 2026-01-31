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

    if platform.system() == 'Windows':
        return str(pypath / 'Scripts' / 'python.exe')

    return str(pypath / 'bin' / 'python')
