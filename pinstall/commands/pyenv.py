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

def update_symlinks(remove_symlinks: bool = False) -> None:
    'Update all symlinks in pyenv versions dir'
    basestr = run('pyenv root', capture=True)
    if not basestr:
        return None

    base = Path(basestr.strip()) / 'versions'
    if not base.exists():
        return None

    # Record of all the existing symlinks and version dirs
    oldlinks = {}
    vers = []
    for path in base.iterdir():
        if all(c in valids for c in path.name):
            if path.is_symlink():
                if remove_symlinks:
                    path.unlink()
                else:
                    oldlinks[path.name] = os.readlink(str(path))
            else:
                vers.append(path)

    if remove_symlinks:
        return None

    # Create a map of all the new major version links
    newlinks_all = defaultdict(list)
    for path in vers:
        namevers = path.name
        while '.' in namevers[:-1]:
            namevers_major = namevers.rsplit('.', maxsplit=1)[0]
            newlinks_all[namevers_major].append(namevers)
            namevers = namevers_major

    newlinks = {k: sorted(v, key=version.parse)[-1] for k, v in
                newlinks_all.items()}

    # Remove all old or invalid existing links
    for name, tgt in oldlinks.items():
        new_tgt = newlinks.get(name)
        if not new_tgt or new_tgt != tgt:
            Path(base / name).unlink()

    # Create all needed new links
    for name, tgt in newlinks.items():
        old_tgt = oldlinks.get(name)
        if not old_tgt or old_tgt != tgt:
            Path(base / name).symlink_to(tgt, target_is_directory=True)

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
        else:
            for newv in updates:
                print(f'### {newv}: installing ...')
                run(f'pyenv install -s {newv}')

    # Ensure we always update all the major version symlinks
    update_symlinks(args.remove_major_symlinks)
    return None
