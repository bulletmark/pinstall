#!/usr/bin/python3
'''
Creates a Python virtual environment using uv.

Runs `uv venv` to create a `.venv/` (optionally for the specified Python
name, or path) then installs all package dependencies from 1)
requirements.txt if present, or 2) from pyproject.toml if present.

[uv](https://github.com/astral-sh/uv) is a new Python installation tool
which is more efficient and **much** faster than `python -m venv` and
`pip`. You can use the `uvenv` command pretty much in place of `venv`
and it will work similarly. At the moment the `uvenv` command is
experimental but if the `uv` tool succeeds, `uvenv` will likely replace
`venv`.
'''
import os
import shutil
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Optional

from ..run import run
from ..pyproj import get_requirements

DEFDIR = '.venv'
DEFEXE = 'python3'
DEFUV = 'uv'
DEFREQ = 'requirements.txt'

def init(parser: ArgumentParser) -> None:
    "Called to add this command's arguments to parser at init"
    parser.add_argument('-d', '--dir', default=DEFDIR,
                        help='directory name to create, default="%(default)s"')
    parser.add_argument('-p', '--python', default=DEFEXE,
                        help='path to python executable, default="%(default)s"')
    parser.add_argument('-u', '--uv',
                        help=f'path to uv executable, default="{DEFUV}"')
    parser.add_argument('-f', '--requirements-file',
                        help=f'default="{DEFREQ}"')
    parser.add_argument('-r', '--no-require', action='store_true',
                        help='don\'t pip install requirements/dependencies')
    parser.add_argument('-i', '--install', nargs='*', metavar='PACKAGE',
                        help='also install (1 or more) given packages')
    parser.add_argument('-R', '--remove', action='store_true',
                        help='just remove any existing venv and finish')
    parser.add_argument('args', nargs='*',
                        help='optional arguments to `uv venv` command'
                        '(add by starting with "--"). See options in '
                        '`uv venv -h`')

def main(args: Namespace) -> Optional[str]:
    'Called to action this command'
    pyexe = args.python
    vdir = Path(args.dir)

    if args.remove:
        if vdir.is_dir():
            print(f'Removing {vdir}/ ..')
            shutil.rmtree(vdir)
            return None
        return f'{vdir}/ does not exist'

    # Ensure uv is installed/available
    uv = args.uv or DEFUV
    version = run(f'{uv} --version', capture=True, ignore_error=True)
    if not version:
        if args.uv:
            return f'Error: uv program not found at "{uv}"'

        return f'Error: {uv} program must be installed, and in your PATH '\
                'or specified with --uv option.'

    if vdir.exists():
        print(f'### Removing existing {vdir}/ ..')
        shutil.rmtree(vdir)

    # Create the venv ..
    os.environ['VIRTUAL_ENV'] = str(vdir)
    opts = f'-p {pyexe} ' + ' '.join(args.args)
    run(f'{uv} venv {opts.rstrip()} {vdir}')
    if not vdir.exists():
        return None

    if not args.no_require:
        reqfile = get_requirements(args.requirements_file, DEFREQ)
        if reqfile:
            if isinstance(reqfile, str):
                return reqfile
            run(f'{uv} pip install -r "{reqfile}"')

    if args.install:
        pkgs = ' '.join(args.install)
        run(f'{uv} pip install {pkgs}')

    return None
