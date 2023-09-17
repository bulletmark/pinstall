#!/usr/bin/python3
'Installer tool for Python programs.'
# Author: Mark Blakeney, Apr 2023.

import argparse
import importlib
import sys
from pathlib import Path

def main():
    'Main code'
    mainparser = argparse.ArgumentParser(description=__doc__)
    subparser = mainparser.add_subparsers(title='Commands',
            dest='func')

    # Iterate over the commands to set up their parsers
    progs = {}
    prog = Path(__file__)
    for modfile in sorted((prog.parent / 'commands').glob('[!_]*.py')):
        name = modfile.stem
        mod = importlib.import_module(f'{prog.stem}.commands.{name}')
        docstr = mod.__doc__.strip().split('\n\n')[0] if mod.__doc__ else None
        parser = subparser.add_parser(name, description=mod.__doc__,
                formatter_class=argparse.RawDescriptionHelpFormatter,
                help=docstr)

        progs[name] = parser.prog

        if hasattr(mod, 'init'):
            mod.init(parser)
        if not hasattr(mod, 'main'):
            mainparser.error(f'"{name}" command must define a main()')

        parser.set_defaults(func=mod.main, parser=parser, name=name)

    args = mainparser.parse_args()

    if not args.func:
        mainparser.print_help()
        return

    args._prog = progs[args.name]

    # Run the command that the user specified
    return args.func(args)

if __name__ == '__main__':
    sys.exit(main())
