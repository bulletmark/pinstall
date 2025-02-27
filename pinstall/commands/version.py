#!/usr/bin/python3
"Reports this program's version."

from __future__ import annotations

import sys
from argparse import Namespace
from pathlib import Path


def main(args: Namespace) -> str | None:
    "Called to action this command"
    if sys.version_info >= (3, 8):
        from importlib.metadata import version
    else:
        from importlib_metadata import version

    try:
        ver = version(Path(sys.argv[0]).stem)
    except Exception:
        ver = 'unknown'

    print(ver)
    return None
