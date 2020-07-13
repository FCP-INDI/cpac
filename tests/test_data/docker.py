import os
import docker

client = docker.from_env()

try:
    client.ping()
except docker.errors.APIError:
    raise "Could not connect to Docker"

def build_image(tag='docker-test'):
    client.images.build(
        path=os.path.dirname(__file__),
        tag=f'fcpindi/c-pac:{tag}',
        quiet=False, rm=True, forcerm=True
    )