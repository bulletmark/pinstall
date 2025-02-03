#!/usr/bin/python3
from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from typing import Any

PYPROJ = 'pyproject.toml'


def _get_pyproj_reqs() -> Any:
    "Return a requirements file built from dependencies in PYPROJ if it exists"
    pyproj = Path(PYPROJ)
    if not pyproj.exists():
        return None

    if sys.version_info >= (3, 11):
        import tomllib
    else:
        import tomli as tomllib  # type: ignore

    with pyproj.open('rb') as fp:
        conf = tomllib.load(fp)

    dependencies = conf.get('project', {}).get('dependencies', [])
    if not dependencies:
        return None

    tmpfile = tempfile.NamedTemporaryFile(prefix=f'{pyproj.stem}.', suffix='.txt')
    tmpfile.writelines(line.encode() + b'\n' for line in dependencies)
    tmpfile.flush()
    return tmpfile


# Keep ths file pointer to prevent it from being deleted
_reqfp = None


def get_requirements(reqname: str, reqname_def: str) -> str | Path:
    "Return the requirements file path, or error message"
    global _reqfp

    if reqname:
        reqfile = Path(reqname)
        if not reqfile.exists():
            return f'Error: file "{reqfile}" does not exist.'
    else:
        reqfile = Path(reqname_def)
        if not reqfile.exists():
            _reqfp = _get_pyproj_reqs()
            reqfile = _reqfp and Path(_reqfp.name)

    return reqfile
