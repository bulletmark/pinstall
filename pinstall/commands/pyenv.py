#!/usr/bin/env python3
'Updates all pyenv python versions and creates links to current major versions.'
import os
import string
from argparse import ArgumentParser, Namespace
from collections import defaultdict
from pathlib import Path
from typing import Optional

from packaging import version

from ..run import run

valids = set(string.digits + '.')

def update_symlinks(args: Namespace) -> None:
    'Update all symlinks in pyenv versions dir'
    basestr = run('pyenv root', capture=True)
    if not basestr:
        return None

    base = Path(basestr.strip()) / 'versions'
    if not base.exists():
        return None

    # Get a record of all the symlinks and versions
    linkmap = {}
    vers = []
    for path in base.iterdir():
        if all(c in valids for c in path.name):
            if path.is_symlink():
                if args.remove_major_symlinks:
                    path.unlink()
                else:
                    linkmap[path.name] = os.readlink(str(path))
            else:
                vers.append(path)

    if args.remove_major_symlinks:
        return None

    # Create a map of all the major version symlinks
    nlinkmap = defaultdict(list)
    for path in vers:
        namevers = path.name
        while '.' in namevers[:-1]:
            namevers_major = namevers.rsplit('.', maxsplit=1)[0]
            nlinkmap[namevers_major].append(namevers)
            namevers = namevers_major

    # Ensure all major links point to the latest version
    for name, nlinks in nlinkmap.items():
        path = base / name
        nlink = sorted(nlinks, key=version.parse)[-1]
        olink = linkmap.get(name)
        if olink != nlink:
            path.unlink(missing_ok=True)
            path.symlink_to(nlink, target_is_directory=True)

        if olink and Path(base / olink).exists():
            del linkmap[name]

    # Delete any old/dead symlinks
    for name in linkmap:
        (base / name).unlink(missing_ok=True)

def init(parser: ArgumentParser) -> None:
    "Called to add this command's arguments to parser at init"
    parser.add_argument('-l', '--list', action='store_true',
                     help='just list latest versions, do not update or purge')
    parser.add_argument('-p', '--purge', action='store_true',
                     help='just purge old versions if later is installed')
    parser.add_argument('-m', '--remove-major-symlinks', action='store_true',
                     help='remove all symlinks to major versions')

def main(args: Namespace) -> Optional[str]:
    'Called to action this command'
    vstr = run('pyenv versions', capture=True)
    if not vstr:
        return None
    versions = [ln.strip() for ln in vstr.splitlines()
                if ' system' not in ln and '->' not in ln]
    outdates = []
    updates = []
    latest = None
    for vers in versions:
        verstr = vers.rsplit('.', maxsplit=1)
        major, minor = verstr if len(verstr) >= 2 else (verstr[0], '')
        if not minor.isdigit():
            print(f'Skipping {vers}')
            continue

        latest = run(f'pyenv latest -k {major}', capture=True)

        if vers == latest:
            print(f'### {vers} up to date')
        elif latest in versions:
            print(f'### {vers} -> {latest} (already installed)')
            outdates.append(vers)
        else:
            print(f'### {vers} -> {latest} (available, but not installed)')
            if latest not in updates:
                updates.append(latest)

    if not args.list:
        if args.purge:
            for overs in outdates:
                print(f'### {overs}: purging ...')
                run(f'pyenv uninstall -f {overs}')
        elif latest:
            for uvers in updates:
                print(f'### {uvers}: updating ...')
                run(f'pyenv install -s {latest}')

    # Ensure we always update all the major version symlinks
    update_symlinks(args)
    return None
