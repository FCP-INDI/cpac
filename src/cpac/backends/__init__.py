from .docker import (
    Docker
)


class BackendMapper(object):

    parameters = {}

    def __init__(self, **kwargs):
        self.parameters = kwargs

    def __call__(self, backend, parent=None):
        return self._clients[backend.__class__](
            backend=backend,
            **self.parameters,
            parent=parent
        )
