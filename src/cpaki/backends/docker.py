from .backend import Backend
import yaml
import docker


class Docker(Backend):

    tag = 'latest'

    def __init__(self, scheduler):
        self.client = docker.from_env()
        try:
            self.client.ping()
        except docker.errors.APIError:
            raise "Could not connect to Docker"
        self.scheduler = scheduler

    def schedule(self, pipeline_config, data_config):
        for subject in data_config:
            self.scheduler.schedule(self, pipeline_config, subject)

    def start(self, pipeline_config, subject):
        container = self.client.containers.run(
            'fcpindi/c-pac:' + self.tag,
            command=['dataset_folder', 'output_folder', 'participant', '--monitoring'],
            detach=True,
            ports={'8080/tcp': None},
            volumes={
                '/home/user1/': {'bind': 'dataset_folder', 'mode': 'ro'},
                '/tmp': {'bind': '/scratch', 'mode': 'rw'},
            }
        )

        return DockerRun(self, pipeline_config, subject, container)


class DockerRun(object):

    def __init__(self, backend, pipeline_config, subject, container):
        self.backend = backend
        self.pipeline_config = pipeline_config
        self.subject = subject
        self.container = container

    def status(self):
        status = self.container.status
        status_map = {
            'created': 'running', 
            'restarting': 'running', 
            'running': 'running', 
            'removing': 'stopped', 
            'paused': 'stopped', 
            'exited': 'stopped', 
            'dead': 'stopped'
        }
        if status in status_map:
            return status_map[status]

        return 'unknown'


class DockerSchedule(object):

    def __init__(self, backend, pipeline_config, subject):
        self.backend = backend
        self.pipeline_config = pipeline_config
        self.subject = subject
        self._run = None

    def start(self):
        self._run = self.backend.start(self.pipeline_config, self.subject)

    def status(self):
        if not self._run:
            return "unstarted"
        
