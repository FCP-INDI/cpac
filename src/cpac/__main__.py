#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import sys

from cpac import __version__
from cpac.backends import Backends

_logger = logging.getLogger(__name__)

# commandline arguments to pass into container after `--`:
clargs = {'group', 'utils'}


class ExtendAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        items = (getattr(namespace, self.dest) or []) + values
        items = [x for n, x in enumerate(items) if x not in items[:n]]
        setattr(namespace, self.dest, items)


def address(str):  # pragma: no cover
    addr, port = str.split(':')
    port = int(port)
    return addr, port


def parse_args(args):
    cwd = os.getcwd()

    parser = argparse.ArgumentParser(
        description='cpac: a Python package that simplifies using C-PAC '
                    '<http://fcp-indi.github.io> containerized images. \n\n'
                    'This commandline interface package is designed to ' 'minimize repetition.\nAs such, nearly all arguments are '
                    'optional.\n\nWhen launching a container, this package '
                    'will try to bind any paths mentioned in \n • the command'
                    '\n • the data configuration\n\nAn example minimal run '
                    'command:\n\tcpac run /path/to/data /path/for/outputs'
                    '\n\nAn example run command with optional arguments:\n\t'
                    'cpac -B /path/to/data/configs:/configs \\\n\t\t'
                    '--image fcpindi/c-pac --tag latest \\\n\t\t'
                    'run /path/to/data /path/for/outputs \\\n\t\t'
                    '--data_config_file /configs/data_config.yml \\\n\t\t'
                    '--save_working_dir\n\n'
                    'Each command can take "--help" to provide additonal '
                    'usage information, e.g.,\n\n\tcpac run --help',
        conflict_handler='resolve',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='cpac {ver}'.format(ver=__version__)
    )
    
    parser.add_argument(
        '-o', '--container_option',
        dest='container_option',
        nargs='*',
        help='parameters and flags to pass through to Docker or Singularity\n'
             '\nThis flag can take multiple arguments so cannot '
             'be\nthe final argument before the command argument (i.e.,\nrun '
             'or any other command that does not start with - or --)\n',
        metavar='OPT'
    )

    parser.add_argument(
        '-B', '--custom_binding',
        dest='custom_binding',
        nargs='*',
        help='directories to bind with a different path in\nthe container '
             'than the real path of the directory.\nOne or more pairs in the ' 'format:\n\treal_path:container_path\n(eg, '
             '/home/C-PAC/run5/outputs:/outputs).\nUse absolute paths for '
             'both paths.\n\nThis flag can take multiple arguments so cannot '
             'be\nthe final argument before the command argument (i.e.,\nrun '
             'or any other command that does not start with - or --)\n'
    )

    parser.add_argument(
        '--platform',
        choices=['docker', 'singularity'],
        help='If neither platform nor image is specified,\ncpac will try '
        'Docker first, then try\nSingularity if Docker fails.'
    )

    parser.add_argument(
        '--image',
        help='path to Singularity image file OR name of Docker image (eg, '
             '"fcpindi/c-pac").\nWill attempt to pull from Singularity Hub or '
             'Docker Hub if not provided.\nIf image is specified but platform '
             'is not, platform is\nassumed to be Singularity if image is a '
             'path or \nDocker if image is an image name.'
    )

    parser.add_argument(
        '--tag',
        help='tag of the Docker image to use (eg, "latest" or "nightly").'
    )

    parser.add_argument(
        '--working_dir',
        default=cwd,
        help='working directory',
        metavar='PATH'
    )

    parser.add_argument(
        '--temp_dir',
        default='/tmp',
        help='directory for temporary files',
        metavar='PATH'
    )

    parser.add_argument(
        '-v',
        '--verbose',
        dest='loglevel',
        help='set loglevel to INFO',
        action='store_const',
        const=logging.INFO
    )

    parser.add_argument(
        '-vv',
        '--very-verbose',
        dest='loglevel',
        help='set loglevel to DEBUG',
        action='store_const',
        const=logging.DEBUG
    )

    subparsers = parser.add_subparsers(dest='command')

    run_parser = subparsers.add_parser(
        'run',
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    help_call = '--help' in sys.argv or '-h' in sys.argv
    run_parser.register('action', 'extend', ExtendAction)
    # run_parser.add_argument('--address', action='store', type=address)

    if not help_call:
        # These positional arguments are required unless we're just getting
        # the helpstring
        run_parser.add_argument(
            'bids_dir'
        )
        run_parser.add_argument(
            'output_dir',
            default=os.path.join(cwd, 'outputs')
        )
        run_parser.add_argument(
            'level_of_analysis',
            choices=['participant', 'group', 'test_config']
        )
    run_parser.add_argument(
        '--data_config_file',
        metavar="PATH"
    )
    run_parser.add_argument(
        'extra_args',
        nargs=argparse.REMAINDER
    )

    group_parser = subparsers.add_parser(
        'group',
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    group_parser.register('action', 'extend', ExtendAction)

    utils_parser = subparsers.add_parser(
        'utils',
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    utils_parser.register('action', 'extend', ExtendAction)

    crash_parser = subparsers.add_parser(
        'crash',
        add_help=True,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    crash_parser.register('action', 'extend', ExtendAction)

    crash_parser.add_argument(
        'crashfile',
        help="path to crashfile"
    )

    parsed, extras = parser.parse_known_args(args)

    parsed.extra_args = [
        *(parsed.extra_args if hasattr(parsed, 'extra_args') else []),
        *extras
    ]

    return parsed


def setup_logging(loglevel):
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel, stream=sys.stdout,
                        format=logformat, datefmt="%Y-%m-%d %H:%M:%S")


def main(args):
    original_args = args
    args = parse_args(args[1:])

    if not args.platform and "--platform" not in original_args:
        if args.image and os.path.exists(args.image):
            args.platform = 'singularity'
        else:
            try:
                main([
                    original_args[0],
                    '--platform',
                    'docker',
                    *original_args[1:]
                ])
            except Exception:  # pragma: no cover
                main([
                    original_args[0],
                    '--platform',
                    'singularity',
                    *original_args[1:]
                ])
            return  # pragma: no cover
    else:
        del original_args

    if any([
        '--data_config_file' in arg for arg in args.extra_args
    ]):
        try:
            args.data_config_file = args.extra_args[
                args.extra_args.index('--data_config_file')+1
            ]
        except ValueError:
            try:
                args.data_config_file = [
                    arg.split(
                        '=',
                        1
                    )[1] for arg in args.extra_args if arg.startswith(
                        '--data_config_file='
                    )
                ][0]
            except Exception:  # pragma: no cover
                raise ValueError(
                    f"""Something about {[
                        arg for arg in args.extra_args if
                        '--data_config_file' in arg
                    ]} is confusing."""
                )
    else:
        args.data_config_file = args.data_config_file if hasattr(
            args,
            'data_config_file'
        ) else None

    args.bids_dir = args.bids_dir if hasattr(
        args,
        'bids_dir'
    ) else 'bids_dir'

    setup_logging(args.loglevel)

    arg_vars = vars(args)
    if args.command == 'run':
        if any([
            '--help' in arg_vars,
            '-h' in arg_vars,
            '--help' in args.extra_args,
            '-h' in args.extra_args
        ]):
            pwd = os.getcwd()
            if arg_vars.get('level_of_analysis') is None:
                arg_vars['level_of_analysis'] = 'participant'
            for arg in ['output_dir', 'bids_dir']:
                if arg_vars.get(arg) is None:
                    arg_vars[arg] = pwd
        Backends(**arg_vars).run(
            flags=args.extra_args,
            **arg_vars
        )

    if args.command in clargs:
        Backends(**arg_vars).clarg(
            args.command,
            flags=args.extra_args,
            **arg_vars
        )

    if args.command == 'crash':
        Backends(**arg_vars).read_crash(
            flags=args.extra_args,
            **arg_vars
        )


def run():
    main(sys.argv)


if __name__ == "__main__":
    run()
