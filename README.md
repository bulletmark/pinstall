## PINSTALL - Installer Tool for Python Programs
[![PyPi](https://img.shields.io/pypi/v/pinstall)](https://pypi.org/project/pinstall/)
[![AUR](https://img.shields.io/aur/version/pinstall)](https://aur.archlinux.org/packages/pinstall/)

This is a simple tool to facilitate installing Python programs on Linux
systems. The following commands are presently implemented, each as an
independent [plugin](pinstall/commands).

The latest documentation and code is available at
https://github.com/bulletmark/pinstall.

## Usage

Type `pinstall` or `pinstall -h` to view the usage summary:

```
usage: pinstall [-h] {venv,status,service} ...

Installer tool for Python programs.

options:
  -h, --help            show this help message and exit

Commands:
  {venv,status,service}
    venv                Creates a Python virtual environment.
    status              Reports systemctl status of services and timers
                        installed from the current directory.
    service             Installs systemd services and corresponding timers.
```

Type `pinstall <command> -h` to see specific help/usage for any
individual command:

### Command `venv`

```
usage: pinstall venv [-h] [-d DIR] [-p PYTHON | -P PYENV]
                        [-f REQUIREMENTS_FILE] [-D] [-r] [-u]
                        [-i [PACKAGE ...]] [-w] [-v]
                        [args ...]

Creates a Python virtual environment.

Runs `python -m venv` (optionally for the specified Python name, or
path, or pyenv Python version) to create a venv; adds a .gitignore to it
to be automatically ignored by git; upgrades the venv with the latest
pip + setuptools + wheel; then installs all packages from
requirements.txt if present.

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
  -D, --install-pyproject
                        install dependencies from pyproject.toml (only if
                        requirements.txt file not present)
  -r, --no-require      don't pip install requirements/dependencies
  -u, --no-upgrade      don't upgrade pip/setuptools in venv
  -i [PACKAGE ...], --install [PACKAGE ...]
                        also install (1 or more) given packages
  -w, --no-wheel        don't install wheel in venv
  -v, --verbose         verbose pip install (can add multiple times to
                        increase verbosity)
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
    PROGTITLE : Upper case of PROG

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

## Command `venv` usage with Pyenv

[Pyenv](https://github.com/pyenv/pyenv) is a popular tool to easily
install and switch between multiple versions of Python. So for example,
you can use `pyenv` + `pinstall` to easily test a Python program with an
older or newer version than your system Python.

E.g. Install Python 3.7 and then create a virtual enviroment (in the
current directory) using it:

```sh
$ pyenv install 3.7
$ pinstall venv -P 3.7
$ venv/bin/python --version
Python 3.7.16
```

Note in this example that [pyenv](https://github.com/pyenv/pyenv)
installed Python 3.7.16 because that was the latest 3.7 version
available (at the time of writing).

## Installation

Arch Linux users can install [pinstall from the
AUR](https://aur.archlinux.org/packages/pinstall).

Python 3.6 or later is required and the [`sudo`](https://www.sudo.ws/)
program must be installed.

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
