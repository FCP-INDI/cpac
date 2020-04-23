import os
import time
import json
import glob
import shutil
import tempfile
import hashlib
import uuid
import copy
import pwd

from base64 import b64decode, b64encode
# from docker.types import Mount
from ..utils import string_types
from .platform import Backend, Result, FileResult

from spython.main import Client
from tornado import httpclient


class Singularity(Backend):

    def __init__(self, **kwargs):
        image = kwargs["image"] if "image" in kwargs else None
        tag = kwargs["tag"] if "tag" in kwargs else None
        print("Loading Ⓢ Singularity")
        if image:
            self.instance = Client.instance(image)
        elif tag:
            self.instance = Client.instance(f"docker://fcpindi/c-pac:{tag}")
        else:
            try:
                self.instance = Client.instance("shub://FCP-INDI/C-PAC")
            except:  # pragma: no cover
            # except docker.errors.APIError:  # pragma: no cover
                raise "Could not connect to Singularity"

    def _bind_volume(self, volumes, local, remote, mode):
        # b = {'bind': remote, 'mode': mode}
        # if local in volumes:
        #     volumes[local].append(b)
        # else:
        #     volumes[local] = [b]
        return(volumes)

    def _load_logging(self, image, bindings):
        import pandas as pd
        import textwrap
        from tabulate import tabulate

        t = pd.DataFrame([
            (i, j['bind'], j['mode']) for i in bindings['volumes'].keys(
            ) for j in bindings['volumes'][i]
        ])
        t.columns = ['local', 'Docker', 'mode']

        print("")

        print(" ".join([
            "Loading Ⓢ",
            image,
            "with these directory bindings:"
        ]))

        print(textwrap.indent(
            tabulate(t, headers='keys', showindex=False),
            '  '
        ))

        print("Logging messages will refer to the Singularity paths.\n")

    def run(self, flags="", **kwargs):

        bindings = self._set_bindings(**kwargs)

        self._load_logging(image, bindings)
        print(bindings)

        return()
        [
            print(o, end="") for o in Client.run(
                self.instance,
                args=" ".join([
                    kwargs['bids_dir'],
                    kwargs['output_dir'],
                    kwargs['level_of_analysis'],
                    flags
                ]).strip(' '),
                stream=True,
                return_result=True
            )
        ]

        # image = ':'.join([
        #     'fcpindi/c-pac',
        #     bindings['tag']
        # ])
        #
        # if isinstance(
        #     kwargs['bids_dir'], str
        # ) and not kwargs['bids_dir'].startswith('s3://'):
        #     b = {
        #         'bind': '/bids_dir',
        #         'mode': 'ro'
        #     }
        #     if kwargs['bids_dir'] in bindings['volumes']:
        #         bindings['volumes'][kwargs['bids_dir']].append(b)
        #     else:
        #         bindings['volumes'][kwargs['bids_dir']] = [b]
        #     bindings['mounts'].append('/bids_dir:{}:ro'.format(
        #         kwargs['bids_dir']
        #     ))
        # else:
        #     kwargs['bids_dir'] = str(kwargs['bids_dir'])
        #
        # command = [i for i in [
        #     kwargs['bids_dir'],
        #     '/outputs',
        #     kwargs['level_of_analysis'],
        #     *flags.split(' ')
        # ] if (i is not None and len(i))]
        #
        self._load_logging(image, bindings)
        #
        # self._run = DockerRun(self.client.containers.run(
        #     image,
        #     command=command,
        #     detach=True,
        #     user=':'.join([
        #         str(bindings['uid']),
        #         str(bindings['gid'])
        #     ]),
        #     volumes=bindings['mounts'],
        #     working_dir='/wd'
        # ))

    def utils(self, flags="", **kwargs):

        # bindings = self._set_bindings(**kwargs)

        [
            print(o, end="") for o in Client.run(
                self.instance,
                args=" ".join([
                    'bids_dir outputs_dir cli -- utils',
                    *flags.split(' ')
                ]).strip(' '),
                stream=True,
                return_result=True
            )
        ]


class SingularityRun(object):

    def __init__():
        pass

    @property
    def status(self):

        return 'unknown'
