class BackendMapper(object):

    parameters = {}

    def __init__(self, *args, **kwargs):
        self.parameters = kwargs

    def __call__(self, backend, parent=None):
        return self._clients[backend.__class__](
            backend=backend,
            **self.parameters,
            parent=parent
        )

def Backends(backend):
    """
    Given a string, return a Backend
    """
    from .docker import Docker
    from .singularity import Singularity

    return(
        {
            'docker': Docker,
            'singularity': Singularity
        }[backend]()
    )
