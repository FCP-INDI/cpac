"""Backend for Apptainer images."""


from cpac.backends.platform import PlatformMeta
from cpac.backends.singularity import Singularity


class Apptainer(Singularity):
    """Backend for Apptainer images."""

    def _set_platform(self):
        """Set metadata for Apptainer platform."""
        self.platform = PlatformMeta("Apptainer", "Ⓐ")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
