#!/usr/bin/python3
'''
Creates a bare-bones Python pyproject.toml file to facilitate
installation by pipx or pip.

Useful when you have an app.py and it's special package dependencies
specified in requirements.txt and want to install that app.py (as
command "app") using pipx or pip but don't have a pyproject.toml (or old
style setup.py). Run this command in the same directory as the files and
it will create a bare-bones ./pyproject.toml file. This will allow you
to install the app using `pipx install .`, or `pip install .` commands.

Your app.py must have a main() function to be called when the app is
run.
'''
import datetime
import getpass
from pathlib import Path
from string import Template

DEFREQ = 'requirements.txt'
PYTOML = 'pyproject.toml'

# Template for pyproject.toml
template = '''\
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
dynamic = [$dependencies]

[[project.authors]]
name = "$user"

[project.scripts]
"$name" = "$pyname:main"
'''

addendum = '''
[tool.setuptools.dynamic]
dependencies = {file = ["$reqfile"]}
'''

def init(parser):
    "Called to add this command's arguments to parser at init"
    parser.add_argument('-f', '--requirements-file',
                        help=f'default="{DEFREQ}"')
    parser.add_argument('app', nargs='?',
                        help='app[.py] or app/ package to '
                        f'create {PYTOML} for. If not specified then '
                        'looks for a single .py file in current directory.')

def main(args):
    'Called to action this command'
    global template

    pytoml = Path(PYTOML)
    if pytoml.exists():
        return f'Error: "{pytoml}" already exists.'

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

    name = file.stem

    if file.is_dir():
        if file.suffix == '.py':
            return f'Error: "{file}" is a directory so can '\
                    'not have a .py extension.'

        file = (file / name).with_suffix('.py')
        pyname = f'{name}.{name}'
    else:
        file = file.with_suffix('.py')
        pyname = name

    if not file.exists():
        return f'Error: "{file}" does not exist.'

    dynamics = []
    if reqfile:
        dynamics.append('dependencies')
        template += addendum
    else:
        template = '\n'.join(line for line in template.splitlines()
                             if not line.startswith('dynamic ')) + '\n'

    template_values = {
        'prog': args._prog,
        'name': name,
        'pyname': pyname,
        'user': getpass.getuser(),
        'dependencies': ', '.join(f'"{d}"' for d in dynamics),
        'reqfile': str(reqfile),
        'date': datetime.datetime.now().isoformat(sep=' ', timespec='seconds'),
    }

    pytoml.write_text(Template(template).substitute(template_values))
    print(f'{pytoml} created.')
