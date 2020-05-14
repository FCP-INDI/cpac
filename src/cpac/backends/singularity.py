import os

from itertools import chain
from spython.main import Client
from subprocess import CalledProcessError

from cpac.backends.platform import Backend

BINDING_MODES = {'ro': 'ro', 'w': 'rw', 'rw': 'rw'}


class Singularity(Backend):
    def __init__(self, **kwargs):
        image = kwargs.get("image")
        tag = kwargs.get("tag")
        pwd = os.getcwd()
        if kwargs.get("working_dir") is not None:
            pwd = kwargs["working_dir"]
            os.chdir(pwd)
        print("Loading Ⓢ Singularity")
        if image and isinstance(image, str) and os.path.exists(image):
            self.image = image
        elif tag and isinstance(tag, str):  # pragma: no cover
            self.image = Client.pull(
                f"docker://{image}:{tag}",
                pull_folder=pwd
            )
        else:  # pragma: no cover
            try:
                self.image = Client.pull(
                    "shub://FCP-INDI/C-PAC",
                    pull_folder=pwd
                )
            except Exception:
                try:
                    self.image = Client.pull(
                        f"docker://fcpindi/c-pac:latest",
                        pull_folder=pwd
                    )
                except Exception:
                    raise OSError("Could not connect to Singularity")
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
                    binding['bind'] if
                    local != binding['bind'] or
                    BINDING_MODES[str(binding['mode'])] != 'rw' else None,
                    BINDING_MODES[str(binding['mode'])] if
                    BINDING_MODES[str(binding['mode'])] != 'rw' else None
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

    def run(self, flags="", **kwargs):
        self._load_logging()
        for o in Client.run(
            self.instance,
            args=" ".join([
                kwargs['bids_dir'],
                kwargs['output_dir'],
                kwargs['level_of_analysis'],
                flags
            ]).strip(' '),
            options=self.options,
            stream=True,
            return_result=True
        ):
            try:
                print(o)
            except CalledProcessError as e:  # pragma: no cover
                print(e)

    def clarg(self, clcommand, flags="", **kwargs):
        """
        Runs a commandline command

        Parameters
        ----------
        clcommand: str

        flags: str

        kwargs: dict
        """
        self._load_logging()
        for o in Client.run(
            self.instance,
            args=" ".join([
                kwargs.get('bids_dir', 'bids_dir'),
                kwargs.get('output_dir', 'output_dir'),
                f'cli -- {clcommand}',
                *flags.split(' ')
            ]).strip(' '),
            options=self.options,
            stream=True,
            return_result=True
        ):
            try:
                print(o)
            except CalledProcessError as e:  # pragma: no cover
                print(e)
