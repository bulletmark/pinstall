#!/usr/bin/python3
"""
Installs or updates the uv program.

Read about uv at https://github.com/astral-sh/uv.
If run this as root/sudo, it installs to /usr/bin/uv otherwise it
installs as your user to $HOME/.local/bin/uv. Requires curl to be
installed.
"""

from __future__ import annotations

import os
from argparse import ArgumentParser, Namespace
from pathlib import Path

from ..run import run

URL = 'https://astral.sh/uv/install.sh'


def get_ver(uv: Path) -> str | None:
    "Run the specified uv to return the version"
    if uv.is_file():
        out = run(f'{uv} --version', capture=True)
        return out.split()[1] if out else None

    return None


def init(parser: ArgumentParser) -> None:
    "Called to add this command's arguments to parser at init"
    parser.add_argument(
        '-r',
        '--remove',
        action='store_true',
        help='just remove any existing uv executable',
    )
    parser.add_argument('-b', '--bindir', help='install to bindir instead of default')
    parser.add_argument(
        '-V',
        '--version',
        action='store_true',
        help='just report version of installed uv executable',
    )


def main(args: Namespace) -> str | None:
    "Called to action this command"
    # Use system bindir if root, otherwise use user bindir
    if args.bindir:
        bindir = Path(args.bindir)
    elif os.getuid() == 0:
        bindir = Path('/', 'usr', 'bin')
        if not bindir.is_dir():
            return f'{bindir} does not exist'
    else:
        bindir = Path('~/.local', 'bin').expanduser()

        if not args.remove and not args.version:
            bindir.mkdir(exist_ok=True, parents=True)

    uv = bindir / 'uv'
    ver_exist = get_ver(uv)

    if args.version:
        if ver_exist:
            print(f'{uv} {ver_exist}')
            return None
        return f'{uv} does not exist.'

    if args.remove:
        uvx = uv.with_name(uv.name + 'x')
        if uvx.is_symlink() or uvx.is_file():
            uvx.unlink()
            print(f'Removed {uvx}')
        if ver_exist:
            uv.unlink()
            print(f'Removed {uv} {ver_exist}')
            return None
        return f'{uv} does not exist.'

    os.environ['UV_INSTALL_DIR'] = str(bindir)
    os.environ['UV_NO_MODIFY_PATH'] = '1'
    run(f'curl -LsSf "{URL}" | sh -s -- -q')

    ver = get_ver(uv)
    if not ver:
        return f'Failed to install {uv}'

    if not ver_exist:
        print(f'Installed {uv} {ver}')
    elif ver_exist != ver:
        print(f'Updated {uv} {ver_exist}->{ver}')
    else:
        print(f'No change {uv} {ver}')

    return None
