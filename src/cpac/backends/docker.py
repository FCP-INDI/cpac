import os
import time
import json
import glob
import docker
import shutil
import tempfile
import hashlib
import uuid
import copy
import pwd

from base64 import b64decode, b64encode
from docker.types import Mount
from tornado import httpclient

from cpac.utils import Permission_mode
from cpac.backends.platform import Backend, Result, FileResult

class Docker(Backend):

    def __init__(self, **kwargs):
        print("Loading 🐳 Docker")
        self.client = docker.from_env()
        try:
            self.client.ping()
        except docker.errors.APIError:  # pragma: no cover
            raise "Could not connect to Docker"
        self.volumes = {}

    def _bind_volume(self, local, remote, mode):
        b = {'bind': remote, 'mode': Permission_mode(mode)}
        if local in self.volumes:
            if remote in [binding['bind'] for binding in self.volumes[local]]:
                for i, binding in enumerate(self.volumes[local]):
                    self.volumes[local][i] = {
                        'bind': remote,
                        'mode': max([self.volumes[local][i]['mode'], b['mode']])
                    }
            else:
                self.volumes[local].append(b)
        else:
            self.volumes[local] = [b]

    def _load_logging(self, image):
        import pandas as pd
        import textwrap
        from tabulate import tabulate

        t = pd.DataFrame([
            (i, j['bind'], j['mode']) for i in self.bindings['volumes'].keys(
            ) for j in self.bindings['volumes'][i]
        ])
        t.columns = ['local', 'Docker', 'mode']

        print("")

        print(" ".join([
            "Loading 🐳",
            image,
            "with these directory bindings:"
        ]))

        print(textwrap.indent(
            tabulate(t, headers='keys', showindex=False),
            '  '
        ))

        print("Logging messages will refer to the Docker paths.\n")

    def run(self, flags="", **kwargs):

        self._set_bindings(**kwargs)

        if isinstance(
            kwargs['bids_dir'], str
        ) and not kwargs['bids_dir'].startswith('s3://'):
            b = {
                'bind': '/bids_dir',
                'mode': 'ro'
            }
            if kwargs['bids_dir'] in self.bindings['volumes']:
                self.bindings['volumes'][kwargs['bids_dir']].append(b)
            else:
                self.bindings['volumes'][kwargs['bids_dir']] = [b]
            self.bindings['mounts'].append('/bids_dir:{}:ro'.format(
                kwargs['bids_dir']
            ))
        else:
            kwargs['bids_dir'] = str(kwargs['bids_dir'])

        kwargs['command'] = [i for i in [
            'run',
            kwargs['bids_dir'],
            '/outputs',
            kwargs['level_of_analysis'],
            *flags.split(' ')
        ] if (i is not None and len(i))]

        self._execute(**kwargs)

    def utils(self, flags="", **kwargs):
        self._set_bindings(**kwargs)

        kwargs['command'] = [i for i in [
            kwargs.get('working_dir', 'NA'),
            '/outputs',
            'cli',
            '--',
            'utils',
            *flags.split(' ')
        ] if (i is not None and len(i))]

        self._execute(**kwargs)


    def _execute(self, command, **kwargs):
        image = ':'.join([
            'fcpindi/c-pac',
            self.bindings['tag']
        ])

        self._load_logging(image)

        self._run = DockerRun(self.client.containers.run(
            image,
            command=command,
            detach=True,
            user=':'.join([
                str(self.bindings['uid']),
                str(self.bindings['gid'])
            ]),
            volumes=self.bindings['mounts'],
            working_dir=kwargs.get('working_dir', '/tmp')
        ))


class DockerRun(object):

    def __init__(self, container):
        self.container = container
        [print(l.decode('utf-8'), end='') for l in self.container.attach(
            logs=True,
            stderr=True,
            stdout=True,
            stream=True
        )]

    @property
    def status(self):
        try:
            self.container.reload()
        except Exception as e:
            return 'stopped'
        status = self.container.status
        status_map = {
            'created': 'starting',
            'restarting': 'running',
            'running': 'running',
            'removing': 'running',
            'paused': 'running',
            'exited': 'success',
            'dead': 'failed'
        }
        if status in status_map:
            return status_map[status]

        return 'unknown'
