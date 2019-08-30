## Code adapted from https://github.com/pycontribs/tendo

import logging
import os
import sys
import tempfile
from multiprocessing import Process

_logger = logging.getLogger(__name__)

if sys.platform != "win32":
    import fcntl


from theodore.scheduler import Scheduler, SCHEDULER_ADDRESS
from theodore.scheduler.api import start
from theodore.backends import docker


class SingleInstance(object):

    def __init__(self):
        self.initialized = False
        self.lockfile = os.path.normpath(tempfile.gettempdir() + '/' + 'theo.lock')
        _logger.debug("SingleInstance lockfile: " + self.lockfile)


    def locked(self):
        return os.path.exists(self.lockfile)

    def __enter__(self):
        if sys.platform == 'win32':
            try:
                if os.path.exists(self.lockfile):
                    os.unlink(self.lockfile)
                self.fd = os.open(
                    self.lockfile,
                    os.O_CREAT | os.O_EXCL | os.O_RDWR
                )
            except OSError:
                t, err, tb = sys.exc_info()
                if err.errno == 13:
                    _logger.error("Another instance is already running, quitting.")
                    raise RuntimeError()
                raise
        else:
            self.fp = open(self.lockfile, 'w')
            self.fp.flush()
            try:
                fcntl.lockf(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except IOError:
                _logger.warning("Another instance is already running, quitting.")
                raise RuntimeError()
        self.initialized = True

    def __exit__(self, *args):
        if not self.initialized:
            return
        try:
            if sys.platform == 'win32':
                if hasattr(self, 'fd'):
                    os.close(self.fd)
                    os.unlink(self.lockfile)
            else:
                fcntl.lockf(self.fp, fcntl.LOCK_UN)
                # os.close(self.fp)
                if os.path.isfile(self.lockfile):
                    os.unlink(self.lockfile)
        except Exception as e:
            _logger.warning(e)
            sys.exit(-1)


def start_scheduler(address=SCHEDULER_ADDRESS, backends=None):

    _logger.debug("Starting server")
    
    backends = backends or ['docker']
    clients = {}
    if 'docker' in backends:
        clients['docker'] = docker.Docker

    with SingleInstance():
        scheduler = Scheduler(clients, clients_priority=backends)
        start(address, scheduler)


def spawn_scheduler(command='theo', address=SCHEDULER_ADDRESS, backends=None):
    
    if SingleInstance().locked():
        return

    _logger.info("Starting server")

    import subprocess

    popen = [
        'python', '-m', 'theodore',
        'scheduler'
    ]

    if address:
        popen += ['--address', '%s:%d' % (address[0], address[1])]

    if backends:
        popen += ['--backend'] + backends

    subprocess.Popen(
        popen,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True
    )
