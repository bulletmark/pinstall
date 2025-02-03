#!/usr/bin/python3
"Common module to run given command"

from __future__ import annotations

import subprocess
import sys


def run(cmd: str, *, capture: bool = False, ignore_error: bool = False) -> str | None:
    "Run given command string"
    if ignore_error:
        cmd += ' 2>/dev/null'

    if capture:
        stdout = subprocess.PIPE
    else:
        stdout = None
        print(f'>>> Running {cmd}')

    try:
        res = subprocess.run(cmd, shell=True, stdout=stdout, universal_newlines=True)
    except Exception as e:
        if not capture and not ignore_error:
            sys.exit(str(e))
        return None

    if res.returncode != 0:
        if not capture and not ignore_error:
            sys.exit(res.returncode)
        return None

    return res.stdout and res.stdout.strip()
