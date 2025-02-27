#!/usr/bin/python3
"""
Creates a bare-bones Python pyproject.toml file to facilitate
installation by pipx or pip.

Useful when you have an app.py and it's special package dependencies
specified in requirements.txt and want to install that app.py (as
command "app") using pipx or pip but don't have a pyproject.toml (or old
style setup.py). Run this command in the same directory as the files and
it will create a bare-bones ./pyproject.toml file. This will allow you
to install the app using `pipx install .`, or `pip install .` commands.

Will also parse PEP 723 dependencies from a script tag in the Python
file.

Your app.py must have a main() function to be called when the app is
run.
"""

from __future__ import annotations

import datetime
import getpass
from argparse import ArgumentParser, Namespace
from pathlib import Path
from string import Template

DEFREQ = 'requirements.txt'
PYTOML = 'pyproject.toml'

# Template for pyproject.toml
template = """\
# DO NOT EDIT. This file was built by "$prog" on $date.
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "$name"
description = "$name installed using $prog"
version = "1.0"
classifiers = [
  "Programming Language :: Python :: 3",
]
dependencies = [$dependencies]

[[project.authors]]
name = "$user"

[project.scripts]
"$name" = "$pyname:main"
"""


def parse_script_tag(file: Path) -> list[str]:
    "Parses PEP723 dependencies from a script tag in a Python file"
    have_script = False
    have_depends = False
    have_end = False
    depends = []
    with file.open() as fp:
        for line in fp:
            line = line.strip()
            if line == '# /// script':
                have_script = True
                continue
            if not have_script:
                continue
            if line == '# dependencies = [':
                have_depends = True
                continue
            if not have_depends:
                continue
            if line == '# ]':
                have_end = True
                break
            line = line.lstrip('#').strip()
            if line and not line.startswith('#'):
                depends.append(line.lstrip('"').rstrip('",'))
    return depends if have_end else []


def init(parser: ArgumentParser) -> None:
    "Called to add this command's arguments to parser at init"
    parser.add_argument('-f', '--requirements-file', help=f'default="{DEFREQ}"')
    parser.add_argument(
        '-o',
        '--overwrite',
        action='store_true',
        help=f'overwrite existing {PYTOML} file',
    )
    parser.add_argument(
        'app',
        nargs='?',
        help='app[.py] or app/ package to '
        f'create {PYTOML} for. If not specified then '
        'looks for a single .py file in current directory.',
    )


def main(args: Namespace) -> str | None:
    "Called to action this command"
    global template

    pytoml = Path(PYTOML)
    if pytoml.exists():
        if not args.overwrite:
            return f'Error: "{pytoml}" already exists.'
        action = 'overwritten'
    else:
        action = 'created'

    # Use user supplied or default requirements file
    if args.requirements_file:
        reqfile = Path(args.requirements_file)
        if not reqfile.exists():
            return f'Error: "{reqfile}" does not exist.'
    else:
        reqfile = Path(DEFREQ)
        if not reqfile.exists():
            reqfile = None

    if not args.app:
        files = list(Path('.').glob('*.py'))
        if not files:
            return 'Error: no .py file in current directory.'
        elif len(files) > 1:
            return 'Error: multiple .py files in current directory.'

        file = Path(files[0])
    else:
        file = Path(args.app)

    if len(file.parts) > 1:
        return f'Error: "{file}" is not a single directory or .py file.'

    if '-' in file.name:
        return f'Error: "{file}" contains a hyphen which is not allowed.'

    filestem = file.stem
    name = filestem.replace('_', '-')

    if file.is_dir():
        if file.suffix == '.py':
            return f'Error: "{file}" is a directory so can not have a .py extension.'

        file = (file / filestem).with_suffix('.py')
        pyname = f'{filestem}.{filestem}'
    else:
        file = file.with_suffix('.py')
        pyname = filestem

    if not file.exists():
        return f'Error: "{file}" does not exist.'

    if reqfile:
        dynamics = [
            ln
            for line in reqfile.read_text().splitlines()
            if (ln := line.strip()) and not ln.startswith('#')
        ]
    else:
        dynamics = parse_script_tag(file)

    depstr = ',\n'.join(f'  "{d}"' for d in dynamics)

    template_values = {
        'prog': args._prog,
        'name': name,
        'pyname': pyname,
        'user': getpass.getuser(),
        'dependencies': ('\n' + depstr + '\n') if depstr else '',
        'date': datetime.datetime.now().isoformat(sep=' ', timespec='seconds'),
    }

    pytoml.write_text(Template(template).substitute(template_values))
    print(f'{pytoml} {action}.')
    return None
