#!/usr/bin/python3
'''
Reports systemctl status of services and timers installed from the
current directory.
'''
import sys
from pathlib import Path

from ..run import run

def init(parser):
    "Called to add this command's arguments to parser at init"
    parser.add_argument('-u', '--user', action='store_true',
                        help='report for user service')
    parser.add_argument('units', nargs='*',
                        help='systemd service file[s]')

def main(args):
    'Called to action this command'
    units = [Path(p) for p in args.units] \
            if args.units else list(Path.cwd().glob('*.service'))

    if not units:
        return 'There are no .service files in this directory'

    cmd = 'systemctl --user status' if args.user else 'systemctl status'

    # Iterate over all specified service files ..
    for unit in units:
        if not unit.suffix.lower() == '.service':
            unit = unit.with_suffix('.service')

        if not unit.exists():
            print(f'### {unit} does not exist', file=sys.stderr)
            continue

        for ext in ('.timer', '.socket'):
            other = unit.with_suffix(ext)
            if other.exists():
                run(f'{cmd} {other.name}')

        run(f'{cmd} {unit.name}')
