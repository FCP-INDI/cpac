#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
import logging

from theodore import __version__

_logger = logging.getLogger(__name__)


class ExtendAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        items = (getattr(namespace, self.dest) or []) + values
        items = [x for n, x in enumerate(items) if x not in items[:n]]
        setattr(namespace, self.dest, items)


def parse_args(args):
    parser = argparse.ArgumentParser(
        description="theodore: a C-PAC utility"
    )

    parser.add_argument(
        '--version',
        action='version',
        version='theodore {ver}'.format(ver=__version__)
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
    scheduler_parser.register('action', 'extend', ExtendAction)
    scheduler_parser.add_argument('--address', action='store', type=str, default='localhost')
    scheduler_parser.add_argument('--port', action='store', type=int, default=8080)
    scheduler_parser.add_argument('--backend', nargs='+', action='extend', choices=['docker', 'singularity'])

    parsed = parser.parse_args(args)

    return parsed


def setup_logging(loglevel):
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel, stream=sys.stdout,
                        format=logformat, datefmt="%Y-%m-%d %H:%M:%S")


def main(args):
    args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug("Script starting...")

    print(args)

    if args.command == 'scheduler':
        from theodore.scheduler import start

        # TODO Backend check for availability

        start(args.address, args.port, args.backend or ['docker'])

    elif args.command == 'run':
        pass
    
    # import docker
    # client = docker.from_env()
    # print(client.containers.run("ubuntu:latest", "echo hello world").decode('ascii'))

    _logger.info("Script ends here")


def run():
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
