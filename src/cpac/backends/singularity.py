import os

from itertools import chain
from spython.main import Client
from subprocess import CalledProcessError
from sys import exc_info

from cpac.backends.platform import Backend, Platform_Meta

BINDING_MODES = {'ro': 'ro', 'w': 'rw', 'rw': 'rw'}


class Singularity(Backend):
    def __init__(self, **kwargs):
        self.platform = Platform_Meta('Singularity', 'Ⓢ')
        image = kwargs.get("image")
        tag = kwargs.get("tag")
        pwd = os.getcwd()
        if kwargs.get("working_dir") is not None:
            pwd = kwargs["working_dir"]
            os.chdir(pwd)
        print(f"Loading {self.platform.symbol} {self.platform.name}")
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

    def _try_to_stream(self, args, stream_command='run'):
        self._bindings_as_option()
        try:
            if stream_command == 'run':
                for line in Client.run(
                    Client.instance(self.image),
                    args=args,
                    options=self.options,
                    stream=True,
                    return_result=True
                ):
                    yield line
            elif stream_command == 'execute':
                for line in Client.execute(
                    self.image,
                    command=args['command'].split(' '),
                    options=self.options,
                    stream=True,
                    quiet=False
                ):
                    yield line
        except CalledProcessError:  # pragma: no cover
            return

    def read_crash(self, crashfile, flags=[], **kwargs):
        self._load_logging()
        self._set_crashfile_binding(crashfile)
        [print(o, end='') for o in self._try_to_stream(
            args={'command': f'nipypecli crash {crashfile}'},
            stream_command='execute'
        )]

    def run(self, flags=[], **kwargs):
        self._load_logging()
        [print(o, end='') for o in self._try_to_stream(
            args=' '.join([
                kwargs['bids_dir'],
                kwargs['output_dir'],
                kwargs['level_of_analysis'],
                *flags
            ]).strip(' ')
        )]

    def clarg(self, clcommand, flags=[], **kwargs):
        """
        Runs a commandline command

        Parameters
        ----------
        clcommand: str

        flags: list

        kwargs: dict
        """
        self._load_logging()
        [print(o, end='') for o in self._try_to_stream(
            args=' '.join([
                kwargs.get('bids_dir', 'bids_dir'),
                kwargs.get('output_dir', 'output_dir'),
                f'cli -- {clcommand}',
                *flags
            ]).strip(' ')
        )]
