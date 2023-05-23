#!/usr/bin/python3
'''
Creates a Python virtual environment.

Runs `python -m venv` (optionally for the specified Python name or path
or pyenv version) to create a venv; adds a .gitignore to it to be
automatically ignored by git; upgrades the venv with the latest pip +
setuptools + wheel; then installs all packages from requirements.txt if
present.
'''
import shutil
from pathlib import Path
from ..run import run

DEFDIR = 'venv'
DEFEXE = 'python3'
DEFREQ = 'requirements.txt'

def init(parser):
    'Called to add arguments to parser at init'
    parser.add_argument('-d', '--dir', default=DEFDIR,
                        help='directory name to create, default="%(default)s"')
    xgroup = parser.add_mutually_exclusive_group()
    xgroup.add_argument('-p', '--python', default=DEFEXE,
                        help='python executable, default="%(default)s"')
    xgroup.add_argument('-P', '--pyenv',
                        help='pyenv version to use, i.e. from `pyenv versions`.')
    parser.add_argument('-f', '--requirements-file',
                        help=f'default="{DEFREQ}"')
    parser.add_argument('-r', '--no-require', action='store_true',
                        help='don\'t pip install packages from '
                        'requirements.txt')
    parser.add_argument('-u', '--no-upgrade', action='store_true',
                        help='don\'t upgrade pip/setuptools in venv')
    parser.add_argument('-w', '--no-wheel', action='store_true',
                        help='don\'t install wheel in venv')
    parser.add_argument('-v', '--verbose', action='count',
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

    if not args.no_require:
        reqfile = Path(args.requirements_file) \
                if args.requirements_file else Path(DEFREQ)

        if reqfile.exists():
            run(f'{pip} install -U -r "{reqfile}"')
        elif args.requirements_file:
            return f'Error: file "{reqfile}" does not exist.'
