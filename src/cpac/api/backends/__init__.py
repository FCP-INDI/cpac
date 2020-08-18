from .docker import DockerSchedule
from .singularity import SingularityBackend

available_backends = {
    'docker': DockerSchedule,
    'singularity': SingularityBackend,
}