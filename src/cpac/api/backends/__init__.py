from .docker import DockerSchedule
from .singularity import SingularityBackend
from .slurm import SLURMBackend

available_backends = {
    'docker': DockerSchedule,
    'singularity': SingularityBackend,
    'slurm': SLURMBackend,
}