"""Given a string, return a Backend."""


def Backends(platform, **kwargs):
    """Given a string, return a Backend."""
    from .apptainer import Apptainer
    from .docker import Docker
    from .singularity import Singularity

    return {"apptainer": Apptainer, "docker": Docker, "singularity": Singularity}[
        platform
    ](**kwargs)
