#!/usr/bin/python3
"""
Creates a Python virtual environment using legacy venv + pip.

Runs `python -m venv` to create a `.venv/` (optionally for the specified
Python name, or path); adds a .gitignore to it to be automatically
ignored by git; upgrades the venv with the latest pip + setuptools +
wheel; then installs all package dependencies from 1) requirements.txt
if present, or 2) from pyproject.toml if present.
"""

from __future__ import annotations

import shutil
from argparse import ArgumentParser, Namespace
from pathlib import Path

from ..getpy import getpy
from ..pyproj import get_requirements
from ..run import run

DEFDIR = '.venv'
DEFEXE = 'python3'
DEFREQ = 'requirements.txt'


def init(parser: ArgumentParser) -> None:
    "Called to add this command's arguments to parser at init"
    parser.add_argument(
        '-d',
        '--dir',
        default=DEFDIR,
        help='directory name to create, default="%(default)s"',
    )
    parser.add_argument(
        '-p',
        '--python',
        default=DEFEXE,
        help='python executable (or venv dir), default="%(default)s"',
    )
    parser.add_argument('-f', '--requirements-file', help=f'default="{DEFREQ}"')
    parser.add_argument(
        '-r',
        '--no-require',
        action='store_true',
        help="don't pip install requirements/dependencies",
    )
    parser.add_argument(
        '-u',
        '--no-upgrade',
        action='store_true',
        help="don't upgrade pip/setuptools in venv",
    )
    parser.add_argument(
        '-i',
        '--install',
        nargs='*',
        metavar='PACKAGE',
        help='also install (1 or more) given packages',
    )
    parser.add_argument(
        '-w',
        '--without-pip',
        action='store_true',
        help="don't install pip or requirements in venv "
        '(i.e. pass --without-pip to python -m venv)',
    )
    parser.add_argument(
        '-W', '--no-wheel', action='store_true', help="don't install wheel in venv"
    )
    parser.add_argument(
        '-R',
        '--remove',
        action='store_true',
        help='just remove any existing venv and finish',
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='count',
        default=0,
        help='verbose pip install (can add multiple times to increase verbosity)',
    )
    parser.add_argument(
        'args',
        nargs='*',
        help='optional arguments to python -m venv '
        '(add by starting with "--"). See options in '
        '`python -m venv -h`',
    )


def main(args: Namespace) -> str | None:
    "Called to action this command"
    pyexe = getpy(args.python)
    vdir = Path(args.dir)

    if args.remove:
        if vdir.is_dir():
            print(f'Removing {vdir}/ ..')
            shutil.rmtree(vdir)
            return None
        return f'{vdir}/ does not exist'

    if '--upgrade' not in args.args and vdir.exists():
        print(f'### Removing existing {vdir}/ ..')
        shutil.rmtree(vdir)

    if args.without_pip and '--without-pip' not in args.args:
        args.args.append('--without-pip')

    # Create the venv ..
    opts = ' ' + ' '.join(args.args)
    run(f'{pyexe} -m venv{opts.rstrip()} {vdir}')
    if not vdir.exists():
        return None

    # Python 3.13+ may create a .gitignore for us, but if not, create one ..
    gitignore = vdir / '.gitignore'
    if not gitignore.exists():
        gitignore.write_text(f'# Automatically created by {args._prog}\n*\n')

    # Next do all pip installs ..
    if '--without-pip' in args.args:
        return None

    pip = str(vdir / 'bin/pip')
    if args.verbose > 0:
        pip += ' -' + 'v' * args.verbose

    if not args.no_upgrade and '--upgrade-deps' not in args.args:
        run(f'{pip} --disable-pip-version-check install -U pip')
        run(f'{pip} install -U setuptools')

    if not args.no_wheel:
        run(f'{pip} install -U wheel')

    if not args.no_require:
        reqfile = get_requirements(args.requirements_file, DEFREQ)
        if reqfile:
            if isinstance(reqfile, str):
                return reqfile
            run(f'{pip} install -U -r "{reqfile}"')

    if args.install:
        pkgs = ' '.join(args.install)
        run(f'{pip} install -U {pkgs}')

    return None
