class BackendMapper(object):

    parameters = {}

    def __init__(self, *args, **kwargs):
        self.parameters = kwargs

    def __call__(self, platform, parent=None):
        return self._clients[platform.__class__](
            platform=platform,
            **self.parameters,
            parent=parent
        )


def Backends(platform, **kwargs):
    """
    Given a string, return a Backend
    """
    from .docker import Docker
    from .singularity import Singularity

    return(
        {
            'docker': Docker,
            'singularity': Singularity
        }[platform](**kwargs)
    )
