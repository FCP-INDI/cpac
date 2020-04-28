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
from .platform import Backend, Result, FileResult

from spython.main import Client
from tornado import httpclient


class Singularity(Backend):

    def __init__(self, **kwargs):
        image = kwargs["image"] if "image" in kwargs else None
        tag = kwargs["tag"] if "tag" in kwargs else None
        print("Loading Ⓢ Singularity")
        if image:
            self.image = image
        elif tag:
            self.image = f"docker://fcpindi/c-pac:{tag}"
        else:
            try:
                self.image = Client.pull(
                    "shub://FCP-INDI/C-PAC",
                    pull_folder=os.getcwd()
                )
            except:  # pragma: no cover
                raise "Could not connect to Singularity"
        self.instance = Client.instance(self.image)

    def _bind_volume(self, local, remote, mode):
        # b = {'bind': remote, 'mode': mode}
        # if local in volumes:
        #     volumes[local].append(b)
        # else:
        #     volumes[local] = [b]
        pass

    def _load_logging(self, bindings):
        import pandas as pd
        import textwrap
        from tabulate import tabulate

        print(bindings['volumes'])

        t = pd.DataFrame([
            (i, j['bind'], j['mode']) for i in bindings['volumes'].keys(
            ) for j in bindings['volumes'][i]
        ])
        t.columns = ['local', 'Singularity', 'mode']

        print("")

        print(" ".join([
            "Loading Ⓢ",
            self.image,
            "with these directory bindings:"
        ]))

        print(textwrap.indent(
            tabulate(t, headers='keys', showindex=False),
            '  '
        ))

        print("Logging messages will refer to the Singularity paths.\n")

    def run(self, flags="", **kwargs):

        self._set_bindings(**kwargs)

        self._load_logging(bindings)
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

    def utils(self, flags="", **kwargs):

        self._set_bindings(**kwargs)

        [
            print(o, end="") for o in Client.run(
                self.instance,
                args=" ".join([
                    kwargs.get('bids_dir', 'bids_dir'),
                    kwargs.get('output_dir', 'output_dir'),
                    'cli -- utils',
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
