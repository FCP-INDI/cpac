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


def address(str):
    addr, port = str.split(':')
    port = int(port)
    return addr, port


def parse_args(args):
    cwd = os.getcwd()

    parser = argparse.ArgumentParser(
        description="cpac: a Python package that simplifies using C-PAC "
                    "<http://fcp-indi.github.io> containerized images."
    )

    parser.add_argument('--platform', choices=['docker', 'singularity'])

    parser.add_argument(
        '--image',
        help='path to Singularity image file. Will attempt to pull from '
             'Singularity Hub or Docker Hub if not provided.'
    )

    parser.add_argument(
        '--tag',
        help='tag of the Docker image to use (eg, "latest" or "nightly"). '
             'Ignored if IMAGE also provided.'
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

    subparsers = parser.add_subparsers(dest='command')

    run_parser = subparsers.add_parser(
        'run',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    run_parser.register('action', 'extend', ExtendAction)
    # run_parser.add_argument('--address', action='store', type=address)

    run_parser.add_argument(
        'bids_dir',
        help="input dataset directory"
    )
    run_parser.add_argument(
        'output_dir',
        default=os.path.join(cwd, 'outputs'),
        help="directory where output files should be stored"
    )
    run_parser.add_argument(
        'level_of_analysis',
        choices=['participant', 'group', 'test_config']
    )
    run_parser.add_argument(
        '--data_config_file',
        help="YAML file containing the location of the data that is to be "
             "processed.",
        metavar="PATH"
    )
    run_parser.add_argument(
        'extra_args',
        nargs=argparse.REMAINDER,
        help="any C-PAC optional arguments "
             "<http://fcp-indi.github.io/docs/user/running>"
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
    command = args[0]
    args = parse_args(args[1:])

    if not args.platform and "--platform" not in original_args:
        try:
            main([
                original_args[0],
                '--platform',
                'docker',
                *original_args[1:]
            ])
        except Exception as e:
            main([
                original_args[0],
                '--platform',
                'singularity',
                *original_args[1:]
            ])
        return()
    else:
        del original_args

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
        Backends(**arg_vars).run(
            flags=" ".join(args.extra_args),
            **arg_vars
        )

    if args.command == 'utils':
        Backends(**arg_vars).utils(
            flags=" ".join(args.extra_args),
            **arg_vars
        )


def run():
    main(sys.argv)


if __name__ == "__main__":
    run()
