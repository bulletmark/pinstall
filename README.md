## PINSTALL - Installer/Utility Tool for Python Programs
[![PyPi](https://img.shields.io/pypi/v/pinstall)](https://pypi.org/project/pinstall/)
[![AUR](https://img.shields.io/aur/version/pinstall)](https://aur.archlinux.org/packages/pinstall/)

This is a simple "swiss-army" tool to facilitate installing Python
programs on Linux systems. The following commands are presently
implemented, each as an independent [plugin](pinstall/commands).

The latest documentation and code is available at
https://github.com/bulletmark/pinstall.

## Usage

Type `pinstall` or `pinstall -h` to view the usage summary:

```
usage: pinstall [-h]
                   {project,pyenv,service,status,uv,uvenv,venv,version} ...

Installer/utility tool for Python programs.

options:
  -h, --help            show this help message and exit

Commands:
  {project,pyenv,service,status,uv,uvenv,venv,version}
    project             Creates a bare-bones Python pyproject.toml file to
                        facilitate installation by pipx or pip.
    pyenv               Updates all pyenv python versions and creates links to
                        current major versions.
    service             Installs systemd services and corresponding timers.
    status              Reports systemctl status of services and timers
                        installed from the current directory.
    uv                  Installs or updates the uv tool.
    uvenv               Creates a Python virtual environment using uv
                        (experimental).
    venv                Creates a Python virtual environment.
    version             Reports this program's version.
```

Type `pinstall <command> -h` to see specific help/usage for any
individual command:

### Command `project`

```
usage: pinstall project [-h] [-f REQUIREMENTS_FILE] [-o] [app]

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

positional arguments:
  app                   app[.py] or app/ package to create pyproject.toml for.
                        If not specified then looks for a single .py file in
                        current directory.

options:
  -h, --help            show this help message and exit
  -f REQUIREMENTS_FILE, --requirements-file REQUIREMENTS_FILE
                        default="requirements.txt"
  -o, --overwrite       overwrite existing pyproject.toml file
```

### Command `pyenv`

```
usage: pinstall pyenv [-h] [-l] [-p] [-m]

Updates all pyenv python versions and creates links to current major versions.

options:
  -h, --help            show this help message and exit
  -l, --list            just list latest versions, do not update or purge
  -p, --purge           just purge old versions if later is installed
  -m, --remove-major-symlinks
                        remove all symlinks to major versions
```

### Command `service`

```
usage: pinstall service [-h] [-u] [-s] [-e] [-r] [units ...]

Installs systemd services and corresponding timers.

Substitutes template strings within each *.service file in the current
directory (and in any corresponding .timer file); installs the
substituted file[s] to the appropriate systemd system (or user) unit
configuration directory; then enables and starts the service (or the
timer).

Template strings can be any of the following:

    HOME      : Home directory path of the invoking user
    USER      : User name of invoking user
    USERID    : Numeric user ID of the invoking user
    GROUPID   : Numeric group ID of the invoking user
    WORKDIR   : Directory path of the service file
    PROGDIR   : Same as WORKDIR
    BASENAME  : Directory name of the service file
    PROG      : Stem name of the service file (i.e. "name" in "name.service")
    PROGTITLE : Upper case PROG

Template strings are specified in .service and .timer files by wrapping
them in hash symbols. Installed copies of these source files have all
instances of template strings replaced by their value. E.g. #HOME#
gets replaced by the user's home directory path.

positional arguments:
  units            systemd service file[s]

options:
  -h, --help       show this help message and exit
  -u, --user       install as user service
  -s, --no-start   do not start service[s]
  -e, --no-enable  do not enable service[s]
  -r, --remove     just uninstall and remove service[s]
```

### Command `status`

```
usage: pinstall status [-h] [-u] [units ...]

Reports systemctl status of services and timers installed from the
current directory.

positional arguments:
  units       systemd service file[s]

options:
  -h, --help  show this help message and exit
  -u, --user  report for user service
```

### Command `uv`

```
usage: pinstall uv [-h] [-r] [-p PREFIX]

Installs or updates the uv tool.

Read about uv at https://github.com/astral-sh/uv.
If run this as root/sudo, it installs to /usr/bin/uv otherwise it
installs as your user to $HOME/.local/bin/uv.

options:
  -h, --help            show this help message and exit
  -r, --remove          just remove any existing uv executable
  -p PREFIX, --prefix PREFIX
                        install to /bin under given system prefix
```

### Command `uvenv`

```
usage: pinstall uvenv [-h] [-d DIR] [-p PYTHON | -P PYENV | -u UV]
                         [-f REQUIREMENTS_FILE] [-r] [-i [PACKAGE ...]] [-R]
                         [args ...]

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

positional arguments:
  args                  optional arguments to `uv venv` command(add by
                        starting with "--"). See options in `uv venv -h`

options:
  -h, --help            show this help message and exit
  -d DIR, --dir DIR     directory name to create, default="venv"
  -p PYTHON, --python PYTHON
                        path to python executable, default="python3"
  -P PYENV, --pyenv PYENV
                        pyenv python version to use, i.e. from `pyenv
                        versions`, e.g. "3.9".
  -u UV, --uv UV        path to uv executable, default="uv"
  -f REQUIREMENTS_FILE, --requirements-file REQUIREMENTS_FILE
                        default="requirements.txt"
  -r, --no-require      don't pip install requirements/dependencies
  -i [PACKAGE ...], --install [PACKAGE ...]
                        also install (1 or more) given packages
  -R, --remove          just remove any existing venv and finish
```

### Command `venv`

```
usage: pinstall venv [-h] [-d DIR] [-p PYTHON | -P PYENV]
                        [-f REQUIREMENTS_FILE] [-r] [-u] [-i [PACKAGE ...]]
                        [-w] [-W] [-R] [-v]
                        [args ...]

Creates a Python virtual environment.

Runs `python -m venv` to create a venv (optionally for the specified
Python name, or path, or pyenv Python version); adds a .gitignore to it
to be automatically ignored by git; upgrades the venv with the latest
pip + setuptools + wheel; then installs all package dependencies from
1) requirements.txt if present, or 2) from pyproject.toml if present.

positional arguments:
  args                  optional arguments to python -m venv (add by starting
                        with "--"). See options in `python -m venv -h`

options:
  -h, --help            show this help message and exit
  -d DIR, --dir DIR     directory name to create, default="venv"
  -p PYTHON, --python PYTHON
                        python executable, default="python3"
  -P PYENV, --pyenv PYENV
                        pyenv python version to use, i.e. from `pyenv
                        versions`, e.g. "3.9".
  -f REQUIREMENTS_FILE, --requirements-file REQUIREMENTS_FILE
                        default="requirements.txt"
  -r, --no-require      don't pip install requirements/dependencies
  -u, --no-upgrade      don't upgrade pip/setuptools in venv
  -i [PACKAGE ...], --install [PACKAGE ...]
                        also install (1 or more) given packages
  -w, --without-pip     don't install pip or requirements in venv (i.e. pass
                        --without-pip to python -m venv)
  -W, --no-wheel        don't install wheel in venv
  -R, --remove          just remove any existing venv and finish
  -v, --verbose         verbose pip install (can add multiple times to
                        increase verbosity)
```

### Command `version`

```
usage: pinstall version [-h]

Reports this program's version.

options:
  -h, --help  show this help message and exit
```

## Command `venv` usage with pyenv

[Pyenv](https://github.com/pyenv/pyenv) is a popular tool to easily
install and switch between multiple versions of Python. So for example,
you can use `pyenv` + `pinstall venv` to easily test a Python program
with an older or newer version than your system Python.

E.g. Install Python 3.7 and then create a virtual enviroment (in the
current directory) using it:

```sh
$ pyenv install 3.7
$ pinstall venv -P 3.7
$ venv/bin/python --version
Python 3.7.17
```

Note in this example that [pyenv](https://github.com/pyenv/pyenv)
installed Python 3.7.17 because that was the latest 3.7 version
available (at the time of writing).

## Management of pyenv versions

[Pyenv](https://github.com/pyenv/pyenv) gives you the handy ability to
install multiple versions of Python. However, there is no easy/quick way
to update all those versions unless you update each manually. So
pinstall offers a `pyenv` command to do this. Just run `pinstall pyenv`
which will check your versions and update any which have a newer minor
version. E.g. if you have 3.7.3 installed and 3.7.4 is available then
`pinstall pyenv` will invoke `pyenv` to install 3.7.4. You can also run
`pinstall pyenv -p` to automatically purge any older/superceded
versions, i.e. to remove 3.7.3 in this example.

`pinstall pyenv` also does something else each time you run it. It
creates or updates major version links. E.g. after installing 3.7.4 as
in the above example, `pinstall pyenv` will also create a link in your
`pyenv` versions directory `3.7 -> 3.7.4`. This allows you to create a
virtual environment in either of two ways:

1. `pinstall venv -P 3.7.4` will create a virtual environment using
   3.7.4 permanently, or:

2. `pinstall venv -P 3.7` will create a virtual environment using the
   link 3.7 which initially points to 3.7.4 but will automatically use
   3.7.5 when/if the minor version gets updated (i.e. after you have
   done a later `pinstall pyenv` to find and install a new 3.7.5). Note
   that python minor (i.e. maintenance) version updates are [always
   backwards
   compatible](https://devguide.python.org/developer-workflow/development-cycle/index.html#maintenance-branches).

Note that whenever you run `pinstall venv` and specify a `-P/--pyenv`
version then pinstall will always first silently update the pyenv links
implicitly to ensure the latest major version links are correct before
creating your new virtual environment.

## Experimental command `uvenv`

[uv](https://github.com/astral-sh/uv) is a new Python installation tool
which is more efficient and **much** faster than `python -m venv` and
`pip`. You can use the `uvenv` command pretty much in place of `venv`
and it will work similarly. At the moment the `uvenv` command is
experimental but if the `uv` tool succeeds, `uvenv` will likely replace
`venv`.

## Installation

Arch Linux users can install [pinstall from the
AUR](https://aur.archlinux.org/packages/pinstall).

Python 3.6 or later is required and the [`sudo`](https://www.sudo.ws/)
program must be installed (to use the `service` command).

Note [pinstall is on PyPI](https://pypi.org/project/pinstall/) so just
ensure that [`pipx`](https://pypa.github.io/pipx/) is installed then
type the following:

```
$ pipx install pinstall
```

To upgrade:

```
$ pipx upgrade pinstall
```

## License

Copyright (C) 2023 Mark Blakeney. This program is distributed under the
terms of the GNU General Public License. This program is free software:
you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation,
either version 3 of the License, or any later version. This program is
distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License at
<http://www.gnu.org/licenses/> for more details.

<!-- vim: se ai syn=markdown: -->
