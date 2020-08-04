#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
import logging

from .. import __version__

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
        description='cpac: a Python package that simplifies using C-PAC.'
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

    scheduler_parser = subparsers.add_parser('scheduler')
    scheduler_parser.add_argument('--address', action='store', type=address, default='localhost:3333')
    # scheduler_parser.register('action', 'extend', ExtendAction)
    # scheduler_parser.add_argument('--backend', nargs='+', action='extend', choices=['docker', 'singularity'])

    # run_parser = subparsers.add_parser('run')
    # run_parser.register('action', 'extend', ExtendAction)
    # run_parser.add_argument('--address', action='store', type=address)
    # run_parser.add_argument('--backend', choices=['docker', 'singularity'])
    # run_parser.add_argument('data_config')
    # run_parser.add_argument('pipeline', nargs='?')

    parsed = parser.parse_args(args)

    return parsed


def setup_logging(loglevel):
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel, stream=sys.stdout,
                        format=logformat, datefmt="%Y-%m-%d %H:%M:%S")


async def start(args):
    from cpac.api.server import start
    from cpac.api.backends.docker import DockerBackend
    from cpac.api.scheduling import Scheduler

    print("Running server")

    backend = DockerBackend(tag='docker-test')
    async with Scheduler(backend) as scheduler:
        await start(args.address, scheduler)
        await scheduler


def main(args):
    command = args[0]
    args = parse_args(args[1:])
    setup_logging(args.loglevel)

    if args.command == 'scheduler':

        import asyncio
        asyncio.run(start(args))

    # elif args.command == 'run':

    #     if not args.address:
    #         from theodore.scheduler.process import spawn_scheduler
    #         spawn_scheduler(args.address, args.backend)

    #     from theodore.scheduler.client import schedule, wait
    #     from theodore.scheduler import SCHEDULER_ADDRESS

    #     scheduler = args.address or SCHEDULER_ADDRESS

    #     schedule(scheduler, args.backend, args.data_config, args.pipeline)


def run():
    main(sys.argv)


if __name__ == "__main__":
    run()