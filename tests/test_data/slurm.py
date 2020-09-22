import docker

client = docker.from_env()
try:
    client.ping()
except docker.errors.APIError:
    raise "Could not connect to Docker"

import re
import os
import tempfile
import logging
import yaml
import time
from datetime import timedelta
from cpac.api.backends.utils import wait_for_port, process

from test_data.singularity import build_image as singularity_build_image

this_dir = os.path.dirname(__file__)
logger = logging.getLogger(__name__)

cluster_image = 'slurm-docker-cluster:19.05.1'
slurm_dir = os.path.join(this_dir, 'slurm_data')

def slurm_config():
    return {
        'host': 'localhost:22222',
        'username': 'root',
        'key': os.path.join(slurm_dir, 'id_rsa'),
        'control': tempfile.mkstemp(prefix='cpacpy-slurm_', suffix='.sock')[1],
        'pip_install': '-e /code',
    }

def start_cluster():
    running_containers = client.containers.list(filters={
        'ancestor': cluster_image,
        'status': 'running'
    })

    config = slurm_config()

    if len(running_containers) == 4:
        logger.info(f'[Fixtures] Using running SLURM cluster')
        return config

    client.images.build(
        path=slurm_dir,
        tag=cluster_image,
        quiet=False, rm=True, forcerm=True
    )

    logger.info(f'[Fixtures] Starting SLURM cluster')

    start_at = time.time()
    process(['docker-compose', 'down', '-v'], cwd=slurm_dir)
    process(['docker-compose', 'up', '-d'], cwd=slurm_dir)

    logger.info(f'[Fixtures] Building Singularity image')
    image = singularity_build_image(type='simg')
    
    wait_for_port(config['host'])

    with open(os.path.join(slurm_dir, 'docker-compose.yml'), 'r') as f:
        compose = yaml.safe_load(f)
    services = compose['services'].keys()

    logger.info(f'[Fixtures] Copying Singularity image to cluster nodes')
    for node in [n for n in services if re.match(r'c[0-9]+', n)]:
        _, container_id, _ = process(['docker-compose', 'ps', '-q', node], cwd=slurm_dir)
        container_id = container_id.decode().strip()
        process(['docker', 'cp', image, f'{container_id}:/opt/cpacpy-singularity_test.simg'])

    time_diff = int(time.time() - start_at)
    logger.info(f'[Fixtures] SLURM cluster up ({timedelta(seconds=time_diff)})')

    return config