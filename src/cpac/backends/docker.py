import os
import time
import json
import glob
import yaml
import docker
import shutil
import tempfile
import hashlib
import uuid
import copy
import pwd

from base64 import b64decode, b64encode

from ..utils import string_types
from .backend import Backend, Result, FileResult

from tornado import httpclient


class Docker(Backend):

    def __init__(self):
        print("Loading 🐳 Docker")
        self.client = docker.from_env()
        try:
            self.client.ping()
        except docker.errors.APIError:
            raise "Could not connect to Docker"

    def _set_bindings(self, **kwargs):

        tag = kwargs.get('tag', None)
        tag = tag if isinstance(tag, str) else 'nightly'

        temp_dir = kwargs.get(
            'temp_dir',
            tempfile.mkdtemp(prefix='cpac_pip_temp_')
        )
        output_dir = kwargs.get(
            'output_dir',
            tempfile.mkdtemp(prefix='cpac_pip_output_')
        )

        volumes = {
            temp_dir: {'bind': '/scratch', 'mode': 'rw'},
            output_dir: {'bind': '/outputs', 'mode':'rw'},
            kwargs.get(
                'working_dir',
                os.getcwd()
            ): {'bind': '/wd', 'mode': 'rw'}
        }


        uid = os.getuid()

        bindings = {
            'gid': pwd.getpwuid(uid).pw_gid,
            'tag': tag,
            'uid': uid,
            'volumes': volumes
        }

        return(bindings)

    def _load_logging(self, image, bindings):
        import pandas as pd
        import textwrap
        from tabulate import tabulate

        t = pd.DataFrame(
            bindings['volumes']
        ).T.rename(columns = {"bind": "Docker"})
        t.index.name = "local"
        t.reset_index(inplace=True)

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

    def run(self, tag='nightly', flags="", **kwargs):

        bindings = self._set_bindings(**kwargs)

        image = ':'.join([
            'fcpindi/c-pac',
            bindings['tag']
        ])

        if isinstance(
            kwargs['bids_dir'], str
        ) and not kwargs['bids_dir'].startswith('s3://'):
            bids_dir = '/bids_dir'
            volumes[kwargs['bids_dir']] = {'bind': bids_dir, 'mode': 'ro'}
        else:
            bids_dir = str(kwargs['bids_dir'])

        command = [i for i in [
            bids_dir,
            '/outputs',
            kwargs['level_of_analysis'],
            *flags.split(' ')
        ] if (i is not None and len(i))]

        self._load_logging(image, bindings)

        _run = DockerRun(self.client.containers.run(
            image,
            command=command,
            detach=True,
            user=':'.join([
                str(bindings['uid']),
                str(bindings['gid'])
            ]),
            volumes=bindings['volumes'],
            working_dir='/wd'
        ))

        _run.container.wait()

    def utils(self, tag='nightly', flags="", **kwargs):

        bindings = self._set_bindings(**kwargs)

        image = ':'.join([
            'fcpindi/c-pac',
            bindings['tag']
        ])

        command = [i for i in [
            kwargs.get('working_dir', 'NA'),
            '/outputs',
            'cli',
            '--',
            'utils',
            *flags.split(' ')
        ] if (i is not None and len(i))]

        self._load_logging(image, bindings)

        _run = DockerRun(self.client.containers.run(
            image,
            command=command,
            detach=False,
            stream=True,
            user=':'.join([
                str(bindings['uid']),
                str(bindings['gid'])
            ]),
            volumes=bindings['volumes'],
            working_dir='/wd'
        ))



class DockerRun(object):

    def __init__(self, container):
        self.container = container
        for l in self.container:
            print(l.decode('utf-8'), end='')

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
