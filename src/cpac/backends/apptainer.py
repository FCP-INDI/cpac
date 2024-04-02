"""Backend for Apptainer images."""
from itertools import chain

from spython.main import Client

from cpac.backends.platform import PlatformMeta
from cpac.backends.singularity import Singularity


class Apptainer(Singularity):
    """Backend for Apptainer images."""

    def __init__(self, **kwargs):
        self.container = None
        self.platform = PlatformMeta("Apptainer", "Ⓐ")
        self.platform.version = Client.version().split(" ")[-1]
        self._print_loading_with_symbol(self.platform.name)
        self.pull(**kwargs, force=False)
        self.options = (
            list(chain.from_iterable(kwargs["container_options"]))
            if bool(kwargs.get("container_options"))
            else []
        )
        if isinstance(self.pipeline_config, str):
            self.config = Client.execute(
                image=self.image,
                command=f"cat {self.pipeline_config}",
                return_result=False,
            )
        else:
            self.config = self.pipeline_config
        kwargs = self.collect_config_bindings(self.config, **kwargs)
        del self.config
        self._set_bindings(**kwargs)
