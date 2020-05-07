#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import sys

from cpac import __version__
from cpac.backends import Backends

_logger = logging.getLogger(__name__)


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
                    '<http://fcp-indi.github.io> containerized images. If no '
                    'platform nor image is specified, cpac will try Docker '
                    'first, then try Singularity if Docker fails.',
        conflict_handler='resolve'
    )

    parser.add_argument('--platform', choices=['docker', 'singularity'])

    parser.add_argument(
        '--image',
        help='path to Singularity image file OR name of Docker image (eg, '
             '"fcpindi/c-pac"). Will attempt to pull from Singularity Hub or '
             'Docker Hub if not provided.'
    )

    parser.add_argument(
        '--tag',
        help='tag of the Docker image to use (eg, "latest" or "nightly"). '
    )

    parser.add_argument(
        '--version',
        action='version',
        version='cpac {ver}'.format(ver=__version__)
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

    parser.add_argument(
        '--working_dir',
        default=cwd,
        help="working directory",
        metavar="PATH"
    )

    parser.add_argument(
        '--temp_dir',
        default='/tmp',
        help="directory for temporary files",
        metavar="PATH"
    )

    parser.add_argument(
        '--output_dir',
        default=os.path.join(cwd, 'outputs'),
        help="directory where output files should be stored",
        metavar="PATH"
    )

    parser.add_argument(
        '-o', '--container_options',
        dest='container_options',
        nargs='+',
        help="parameters and flags to pass through to Docker or Singularity",
        metavar="OPT"
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

    utils_parser = subparsers.add_parser(
        'utils',
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    utils_parser.register('action', 'extend', ExtendAction)

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
            flags=' '.join(args.extra_args),
            **arg_vars
        )

    if args.command == 'utils':
        Backends(**arg_vars).utils(
            flags=' '.join(args.extra_args),
            **arg_vars
        )


def run():
    main(sys.argv)


if __name__ == "__main__":
    run()
