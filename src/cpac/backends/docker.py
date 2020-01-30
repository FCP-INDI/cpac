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

from base64 import b64decode, b64encode

from ..utils import string_types
from .backend import Backend, Result, FileResult

from tornado import httpclient


class Docker(Backend):

    def __init__(self):
        self.client = docker.from_env()
        print('a')
        try:
            self.client.ping()
        except docker.errors.APIError:
            raise "Could not connect to Docker"

    def run(self, tag='nightly', flags="", **kwargs):

        volumes = {
            kwargs['temp_dir']: {'bind': '/scratch', 'mode': 'rw'},
            kwargs['output_dir']: {'bind': '/outputs', 'mode':'rw'},
            kwargs['working_dir']: {'bind': '/wd', 'mode': 'rw'}
        }

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

        print(command)
        print(volumes)
        print(tag)
        print(':'.join([
            'fcpindi/c-pac',
            tag if isinstance(tag, str) else 'nightly'
        ]))

        _run = DockerRun(self.client.containers.run(
            ':'.join([
                'fcpindi/c-pac',
                tag if isinstance(tag, str) else 'nightly'
            ]),
            command=command,
            detach=False,
            user=os.getuid(),
            volumes=volumes,
            working_dir='/wd'
        ))

        print('a')
        _run.container.wait()
        print('b')


class DockerRun(object):

    def __init__(self, container):
        self.container = container

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
