#!/usr/bin/python3
'''
Creates a Python virtual environment using uv (experimental).

Runs `uv venv` to create a venv (optionally for the specified
Python name, or path, or pyenv Python version) then installs all package
dependencies from 1) requirements.txt if present, or 2) from
pyproject.toml if present.

[uv](https://github.com/astral-sh/uv) is a new Python installation tool
which is more efficient and **much** faster than `python -m venv` and
`pip`. You can use the `uvenv` command pretty much in place of `venv`
and it will work similarly. At the moment the `uvenv` command is
experimental but if the `uv` tool succeeds, `uvenv` will likely replace
`venv`.
'''
import os
import shutil
import sys
import tempfile
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any, Optional

from ..run import run
from . import pyenv

DEFDIR = 'venv'
DEFEXE = 'python3'
DEFUV = 'uv'
DEFREQ = 'requirements.txt'
PYPROJ = 'pyproject.toml'

def get_pyproj_reqs() -> Any:
    'Return a requirements file built from dependencies in PYPROJ if it exists'
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

    tmpfile = tempfile.NamedTemporaryFile(prefix=f'{pyproj.stem}.',
                                          suffix='.txt')
    tmpfile.writelines(line.encode() + b'\n' for line in dependencies)
    tmpfile.flush()
    return tmpfile

def init(parser: ArgumentParser) -> None:
    "Called to add this command's arguments to parser at init"
    parser.add_argument('-d', '--dir', default=DEFDIR,
                        help='directory name to create, default="%(default)s"')
    xgroup = parser.add_mutually_exclusive_group()
    xgroup.add_argument('-p', '--python', default=DEFEXE,
                        help='path to python executable, default="%(default)s"')
    xgroup.add_argument('-P', '--pyenv',
                        help='pyenv python version to use, '
                        'i.e. from `pyenv versions`, e.g. "3.9".')
    xgroup.add_argument('-u', '--uv',
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
    if args.pyenv:
        pyenv_root = run('pyenv root', capture=True)
        if not pyenv_root:
            return 'Error: Can not find pyenv. Is it installed?'

        # Since we are about to use pyenv, make sure the links are up to
        # date
        pyenv.update_symlinks()

        pyenv_version = run(f'pyenv latest {args.pyenv}', capture=True,
                            ignore_error=True)
        if not pyenv_version:
            return f'Error: no pyenv version {args.pyenv} installed.'

        pyexe_path = Path(pyenv_root, 'versions', pyenv_version,
                          'bin', 'python')
        if not pyexe_path.exists():
            return f'Can not determine pyenv version for {args.pyenv}'

        pyexe = str(pyexe_path)
    else:
        pyexe = args.python

    vdir = Path(args.dir)

    if args.remove:
        if vdir.exists():
            shutil.rmtree(vdir)
        return None

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
        if args.requirements_file:
            reqfile = Path(args.requirements_file)
            if not reqfile.exists():
                return f'Error: file "{reqfile}" does not exist.'
        else:
            reqfile = Path(DEFREQ)
            if not reqfile.exists():
                fp = get_pyproj_reqs()
                reqfile = fp and Path(fp.name)

        if reqfile:
            run(f'{uv} pip install -r "{reqfile}"')

    if args.install:
        pkgs = ' '.join(args.install)
        run(f'{uv} pip install {pkgs}')

    return None
