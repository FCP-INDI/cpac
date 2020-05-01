import os
import time
import json
import glob
import shutil
import tempfile
import hashlib
import uuid
import copy

from base64 import b64decode, b64encode
from itertools import chain
from spython.main import Client
from subprocess import CalledProcessError
from tornado import httpclient

from cpac.backends.platform import Backend

BINDING_MODES = {'ro': 'ro', 'w': 'rw', 'rw': 'rw'}

class Singularity(Backend):

    def __init__(self, **kwargs):
        image = kwargs["image"] if "image" in kwargs else "fcpindi/c-pac"
        tag = kwargs["tag"] if "tag" in kwargs else None
        print("Loading Ⓢ Singularity")
        if image and os.path.exists(image):
            self.image = image
        elif tag:
            self.image = f"docker://{image}:{tag}"
        else:
            try:
                self.image = Client.pull(
                    "shub://FCP-INDI/C-PAC",
                    pull_folder=os.getcwd()
                )
            except:
                try:
                    self.image = f"docker://fcpindi/c-pac:latest"
                except:  # pragma: no cover
                    raise "Could not connect to Singularity"
        self.instance = Client.instance(self.image)
        self.volumes = {}
        self.options = list(chain.from_iterable(kwargs[
            "container_options"
        ])) if bool(kwargs.get("container_options")) else []
        self._set_bindings(**kwargs)

    def _bindings_as_option(self):
        self.options += (
            ['-B', ','.join((chain.from_iterable([[
                ':'.join([b for b in [
                    local,
                    binding['bind'] if \
                    local!=binding['bind'] or \
                    BINDING_MODES[str(binding['mode'])]!='rw' else None,
                    BINDING_MODES[str(binding['mode'])] if \
                    BINDING_MODES[str(binding['mode'])]!='rw' else None
                ] if b is not None]) for binding in self.volumes[local]
            ] for local in self.volumes])))]
        )

    def _load_logging(self):
        import pandas as pd
        import textwrap
        from tabulate import tabulate

        t = pd.DataFrame([(
                i,
                j['bind'],
                BINDING_MODES[str(j['mode'])]
            ) for i in self.bindings['volumes'].keys(
            ) for j in self.bindings['volumes'][i]
        ])
        t.columns = ['local', 'Singularity', 'mode']

        print(" ".join([
            "Loading Ⓢ",
            self.image,
            "with these directory bindings:"
        ]))

        print(textwrap.indent(
            tabulate(t, headers='keys', showindex=False),
            '  '
        ))

        print("Logging messages will refer to the Singularity paths.")

    def _try_to_stream(self, args, options):
        try:
            yield from next(
                Client.run(
                    self.instance,
                    args=args,
                    options=options,
                    stream=True,
                    return_result=True
                )
            )
        except Exception as e:
            raise(e)

    def run(self, flags="", **kwargs):
        self._load_logging()
        print(" ".join([
            kwargs['bids_dir'],
            kwargs['output_dir'],
            kwargs['level_of_analysis'],
            flags
        ]).strip(' '))
        [
            print(o, end="") for o in self._try_to_stream(
                args=" ".join([
                    kwargs['bids_dir'],
                    kwargs['output_dir'],
                    kwargs['level_of_analysis'],
                    flags
                ]).strip(' '),
                options=self.options
            )
        ]

    def utils(self, flags="", **kwargs):
        self._load_logging()
        print(" ".join([
            kwargs.get('bids_dir', 'bids_dir'),
            kwargs.get('output_dir', 'output_dir'),
            'cli -- utils',
            *flags.split(' ')
        ]).strip(' '))
        [
            print(o, end="") for o in self._try_to_stream(
                args=" ".join([
                    kwargs.get('bids_dir', 'bids_dir'),
                    kwargs.get('output_dir', 'output_dir'),
                    'cli -- utils',
                    *flags.split(' ')
                ]).strip(' '),
                options=self.options
            )
        ]