#!/usr/bin/python3
'''
Creates a Python virtual environment.

Runs `python -m venv` to create a venv (optionally for the specified
Python name, or path, or pyenv Python version); adds a .gitignore to it
to be automatically ignored by git; upgrades the venv with the latest
pip + setuptools + wheel; then installs all package dependencies from
1) requirements.txt if present, or 2) from pyproject.toml if present.
'''
import shutil
import sys
import tempfile
from pathlib import Path

from ..run import run

DEFDIR = 'venv'
DEFEXE = 'python3'
DEFREQ = 'requirements.txt'
PYPROJ = 'pyproject.toml'

def get_pyproj_reqs():
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

def init(parser):
    "Called to add this command's arguments to parser at init"
    parser.add_argument('-d', '--dir', default=DEFDIR,
                        help='directory name to create, default="%(default)s"')
    xgroup = parser.add_mutually_exclusive_group()
    xgroup.add_argument('-p', '--python', default=DEFEXE,
                        help='python executable, default="%(default)s"')
    xgroup.add_argument('-P', '--pyenv',
                        help='pyenv python version to use, '
                        'i.e. from `pyenv versions`, e.g. "3.9".')
    parser.add_argument('-f', '--requirements-file',
                        help=f'default="{DEFREQ}"')
    parser.add_argument('-r', '--no-require', action='store_true',
                        help='don\'t pip install requirements/dependencies')
    parser.add_argument('-u', '--no-upgrade', action='store_true',
                        help='don\'t upgrade pip/setuptools in venv')
    parser.add_argument('-i', '--install', nargs='*', metavar='PACKAGE',
                        help='also install (1 or more) given packages')
    parser.add_argument('-w', '--no-wheel', action='store_true',
                        help='don\'t install wheel in venv')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='verbose pip install (can add multiple times to '
                        'increase verbosity)')
    parser.add_argument('args', nargs='*',
                        help='optional arguments to python -m venv '
                        '(add by starting with "--"). See options in '
                        '`python -m venv -h`')

def main(args):
    'Called to action this command'
    if args.pyenv:
        pyenv_root = run('pyenv root', capture=True)
        if not pyenv_root:
            return 'Error: Can not find pyenv. Is it installed?'

        basedir = Path(pyenv_root, 'versions')
        pydir = basedir / args.pyenv

        if not pydir.exists():
            # Given specific version does not exist, get latest version
            from looseversion import LooseVersion as Version
            try:
                versions = sorted(basedir.glob(f'{args.pyenv}[-.]*'),
                                key=lambda x: Version(x.name))
            except Exception:
                return f'Can not determine pyenv version for {args.pyenv}'

            if not versions:
                return f'Error: no pyenv version {args.pyenv} installed.'

            pydir = versions[-1]

        pyexe = str(pydir / 'bin/python')
    else:
        pyexe = args.python

    vdir = Path(args.dir)
    if '--upgrade' not in args.args and vdir.exists():
        print(f'### Removing existing {vdir}/ ..')
        shutil.rmtree(vdir)

    # Create the venv ..
    opts = ' ' + ' '.join(args.args)
    run(f'{pyexe} -m venv{opts.rstrip()} {vdir}')
    if not vdir.exists():
        return

    text = f'# Automatically created by {args._prog}\n*'
    (Path(vdir) / '.gitignore').write_text(text)

    # Next do all pip installs ..
    if '--without-pip' in args.args:
        return

    pip = str(vdir / 'bin/pip')
    if args.verbose > 0:
        pip += ' -' + 'v' * args.verbose

    if not args.no_upgrade and '--upgrade-deps' not in args.args:
        run(f'{pip} --disable-pip-version-check install -U pip')
        run(f'{pip} install -U setuptools')

    if not args.no_wheel:
        run(f'{pip} install -U wheel')

    if args.install:
        pkgs = ' '.join(args.install)
        run(f'{pip} install -U {pkgs}')

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
            run(f'{pip} install -U -r "{reqfile}"')
