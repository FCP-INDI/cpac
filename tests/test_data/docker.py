import os
import docker

client = docker.from_env()

try:
    client.ping()
except docker.errors.APIError:
    raise "Could not connect to Docker"

image = None

def build_image(tag='docker-test'):
    global image
    if image is None:
        client.images.build(
            path=os.path.dirname(__file__),
            tag='fcpindi/c-pac:docker-test',
            quiet=False, rm=True, forcerm=True
        )
        image = 'fcpindi/c-pac:docker-test'

    return image