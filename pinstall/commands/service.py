#!/usr/bin/python3
'''
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
'''
import getpass
import os
import sys
from pathlib import Path
from pwd import getpwnam

from ..run import run

def init(parser):
    "Called to add this command's arguments to parser at init"
    parser.add_argument('-u', '--user', action='store_true',
                        help='install as user service')
    parser.add_argument('-s', '--no-start', action='store_true',
                        help='do not start service[s]')
    parser.add_argument('-e', '--no-enable', action='store_true',
                        help='do not enable service[s]')
    parser.add_argument('-r', '--remove', action='store_true',
                        help='just uninstall and remove service[s]')
    parser.add_argument('units', nargs='*',
                        help='systemd service file[s]')

def remove_unit(args, unit):
    'Remove given unit file'
    if not unit.exists():
        return False

    unit.unlink()
    print(f'### {unit} removed')

    # Delete all empty parent dirs if user ..
    if args.user:
        while True:
            unit = unit.parent
            if any(unit.iterdir()):
                break
            try:
                unit.parent.rmdir()
            except Exception:
                print(f'### Warning: failed to remove {unit} directory',
                      file=sys.stderr)
            else:
                print(f'### {unit} directory removed')

    return True

def create_unit(args, templdata, sysdpath, unit):
    'Create given unit file'
    target = sysdpath / unit.name
    print(f'### Creating unit file {target}')
    templdata['PROG'] = unit.stem
    templdata['PROGTITLE'] = unit.stem.upper()
    sysdpath.parent.mkdir(exist_ok=True)

    # Read unit file and replace all template values
    content = unit.read_text()
    for key, val in templdata.items():
        content = content.replace(f'#{key}#', val)

    # If installing as user then must remove User line
    if args.user:
        content = '\n'.join(ln for ln in content.splitlines()
                           if not ln.startswith('User='))

    if not target.exists():
        print(f'### {target} has been installed')
        target.write_text(content)
    elif content != target.read_text():
        print(f'### {target} has been updated')
        target.write_text(content)
    else:
        print(f'### {target} has not changed')
        return False

    return True

def main(args):
    'Called to action this command'
    userid = os.getuid()
    if not args.user:
        # Not user mode so if not yet running as root then re-invoke
        # ourself as root ..
        if userid != 0:
            return run('sudo ' + ' '.join(sys.argv))

        # Running as root from here ..
        user = os.getenv('SUDO_USER')
        if not user:
            return 'Error: must run using sudo to identify user'

        sysdpath = Path('/etc/systemd/system')
    else:
        user = getpass.getuser()
        cdir = os.getenv('XDG_CONFIG_HOME', '~/.config')
        sysdpath = Path(cdir).expanduser() / 'systemd' / 'user'

    units = [Path(p) for p in args.units] \
            if args.units else list(Path.cwd().glob('*.service'))

    if not units:
        return 'There are no .service files in this directory'

    pw = getpwnam(user)

    # Build template dict
    templdata = {}
    templdata['USER'] = user
    templdata['USERID'] = str(pw.pw_uid)
    templdata['GROUPID'] = str(pw.pw_gid)
    templdata['HOME'] = pw.pw_dir

    sysctl = 'systemctl --user' if args.user else 'systemctl'
    change = False

    # Iterate over all specified service files ..
    for unit in units:
        if not unit.suffix.lower() == '.service':
            unit = unit.with_suffix('.service')

        if not unit.exists():
            print(f'### {unit} does not exist', file=sys.stderr)
            continue

        if args.remove:
            for ext in ('.timer', '.socket', '.service'):
                name = unit.stem + ext
                run(f'{sysctl} disable --now {name}', capture=True,
                    ignore_error=True)
                if remove_unit(args, sysdpath / name):
                    change = True
            continue

        workdir = unit.parent
        templdata['WORKDIR'] = templdata['PROGDIR'] = str(workdir)
        templdata['BASENAME'] = workdir.name

        for ext in ('.timer', '.socket'):
            other = unit.with_suffix(ext)
            if other.exists():
                create_unit(args, templdata, sysdpath, unit)
                unit = other
                break

        if create_unit(args, templdata, sysdpath, unit):
            change = True

        if 'By=' in unit.read_text():
            if not args.no_enable:
                run(f'{sysctl} enable {unit.name}')

            if not args.no_start:
                run(f'{sysctl} restart {unit.name}')
                run(f'{sysctl} --no-pager status {unit.name}')

    if change:
        run(f'{sysctl} daemon-reload')
