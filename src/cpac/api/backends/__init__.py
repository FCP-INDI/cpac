from .docker import DockerBackend
from .singularity import SingularityBackend
from .slurm import SLURMBackend

available_backends = {
    'docker': DockerBackend,
    'singularity': SingularityBackend,
    'slurm': SLURMBackend,
}