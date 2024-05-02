#!/usr/bin/python3
import platform
from pathlib import Path
from typing import Optional

def getpy(pyfile: Optional[str]) -> Optional[str]:
    if not pyfile:
        return None

    pypath = Path(pyfile)
    if not pypath.is_dir():
        return pyfile

    binpath = 'Scripts' if platform.system() == 'Windows' else 'bin'
    return str(pypath / binpath / 'python')
