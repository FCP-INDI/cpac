#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import sys

from cpac import __version__

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
    parser = argparse.ArgumentParser(
        description="cpac: a Python package that wraps C-PAC "
                    "<http://fcp-indi.github.io>"
    )

    parser.add_argument(
        '--version',
        action='version',
        version='cpac {ver}'.format(ver=__version__)
    )

    parser.add_argument(
        '-v',
        '--verbose',
        dest="loglevel",
        help="set loglevel to INFO",
        action='store_const',
        const=logging.INFO
    )

    parser.add_argument(
        '-vv',
        '--very-verbose',
        dest="loglevel",
        help="set loglevel to DEBUG",
        action='store_const',
        const=logging.DEBUG
    )

    subparsers = parser.add_subparsers(dest='command')

    # scheduler_parser = subparsers.add_parser('scheduler')
    # scheduler_parser.register('action', 'extend', ExtendAction)
    # scheduler_parser.add_argument('--address', action='store', type=address, default='localhost:3333')
    # scheduler_parser.add_argument('--backend', nargs='+', action='extend', choices=['docker', 'singularity'])

    run_parser = subparsers.add_parser('run', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    run_parser.register('action', 'extend', ExtendAction)
    run_parser.add_argument('--temp_dir', default='/tmp', help="directory for temporary files", metavar="PATH")
    run_parser.add_argument('--working_dir', default=os.getcwd(), help="working directory", metavar="PATH")
    run_parser.add_argument('--address', action='store', type=address)
    run_parser.add_argument('--bids_dir', help="input dataset directory", metavar="PATH")
    run_parser.add_argument('--output_dir', default='/outputs', help="directory where output files should be stored", metavar="PATH")
    # run_parser.add_argument('--backend', choices=['docker']) # TODO: Add Singularity
    run_parser.add_argument('level_of_analysis', choices=['participant', 'group', 'test_config'])
    run_parser.add_argument('args', nargs=argparse.REMAINDER, help="any C-PAC optional arguments <http://fcp-indi.github.io/docs/user/quick>")

    parsed = parser.parse_args(args)

    # Set backend automatically while there's only one supported backend
    parsed.backend = 'docker'

    return parsed


def setup_logging(loglevel):
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel, stream=sys.stdout,
                        format=logformat, datefmt="%Y-%m-%d %H:%M:%S")


def main(args):
    command = args[0]
    args = parse_args(args[1:])
    setup_logging(args.loglevel)

    if args.command == 'scheduler':
        from cpac.scheduler.process import start_scheduler
        start_scheduler(args.address, args.backend)

    elif args.command == 'run':

        if not args.address:
            from cpac.scheduler.process import spawn_scheduler
            spawn_scheduler(args.address, args.backend)

        from cpac.scheduler.client import schedule, wait
        from cpac.scheduler import SCHEDULER_ADDRESS

        scheduler = args.address or SCHEDULER_ADDRESS

        schedule(
            scheduler,
            args.backend,
            args.data_config_file if hasattr(
                args,
                'data_config_file'
            ) else None,
            args.pipeline_file if hasattr(
                args,
                'pipeline_file'
            ) else None
        )


def run():
    main(sys.argv)


if __name__ == "__main__":
    run()
