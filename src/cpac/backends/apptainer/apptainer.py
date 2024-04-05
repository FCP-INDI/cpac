"""Backend for Apptainer images."""
from spython import main as spython_main
from spython.main.base import command

from cpac.backends.platform import PlatformMeta
from cpac.backends.singularity import Singularity
from .spython import get_client, init_command


class Apptainer(Singularity):
    """Backend for Apptainer images."""

    def _set_platform(self):
        """Set metadata for Apptainer platform."""
        self.platform = PlatformMeta("Apptainer", "Ⓐ")
        # use apptainer instead of singularity in spython
        command.init_command = init_command
        spython_main.get_client = get_client
        spython_main.base.Client._init_command = init_command

    def __init__(self, **kwargs):
        self._set_platform()
        super().__init__(**kwargs)
