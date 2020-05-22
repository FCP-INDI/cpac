import docker

from cpac.backends.platform import Backend, Platform_Meta


class Docker(Backend):
    def __init__(self, **kwargs):
        self.platform = Platform_Meta('Docker', '🐳')
        print(f"Loading {self.platform.symbol} {self.platform.name}")
        self.client = docker.from_env()
        try:
            self.client.ping()
        except docker.errors.APIError:  # pragma: no cover
            raise OSError(f"Could not connect to {self.platform.name}")
        self.volumes = {}
        self._set_bindings(**kwargs)
        self.docker_kwargs = {}
        if isinstance(kwargs.get('container_options'), list):
            for opt in kwargs['container_options']:
                if '=' in opt or ' ' in opt:
                    delimiter = min([
                        i for i in [
                            opt.find('='), opt.find(' ')
                        ] if i > 0
                    ])
                    k = opt[:delimiter].lstrip('-').replace('-', '_')
                    v = opt[delimiter+1:].strip('"').strip("'")
                    if k in self.docker_kwargs:
                        if isinstance(self.docker_kwargs[k], list):
                            self.docker_kwargs[k].append(v)
                        else:
                            self.docker_kwargs[k] = [self.docker_kwargs[k], v]
                    else:
                        self.docker_kwargs[k] = v

    def read_crash(self, crashfile, flags=[], **kwargs):
        self._set_crashfile_binding(crashfile)
        self.docker_kwargs['entrypoint'] = f'nipypecli crash {crashfile}'
        self._execute(command=flags)

    def run(self, flags=[], **kwargs):
        kwargs['command'] = [i for i in [
            kwargs['bids_dir'],
            kwargs['output_dir'],
            kwargs['level_of_analysis'],
            *flags
        ] if (i is not None and len(i))]
        self._execute(**kwargs)

    def clarg(self, clcommand, flags=[], **kwargs):
        """
        Runs a commandline command

        Parameters
        ----------
        clcommand: str

        flags: list

        kwargs: dict
        """
        kwargs['command'] = [i for i in [
            kwargs.get('bids_dir', kwargs.get('working_dir', '/tmp')),
            kwargs.get('output_dir', '/outputs'),
            'cli',
            '--',
            clcommand,
            *flags
        ] if (i is not None and len(i))]
        self._execute(**kwargs)

    def _execute(self, command, **kwargs):
        self.image = ':'.join([
            kwargs['image'] if kwargs.get(
                'image'
            ) is not None else 'fcpindi/c-pac',
            self.bindings['tag'] if self.bindings.get(
                'tag'
            ) is not None else 'latest'
        ])

        self._load_logging()

        self._run = DockerRun(self.client.containers.run(
            self.image,
            command=command,
            detach=True,
            user=':'.join([
                str(self.bindings['uid']),
                str(self.bindings['gid'])
            ]),
            volumes=self.bindings['mounts'],
            working_dir=kwargs.get('working_dir', '/tmp'),
            **self.docker_kwargs
        ))


class DockerRun(object):

    def __init__(self, container):
        self.container = container
        [print(l.decode('utf-8'), end='') for l in self.container.attach(
            logs=True,
            stderr=True,
            stdout=True,
            stream=True
        )]

    @property
    def status(self):
        try:
            self.container.reload()
        except Exception:
            return 'stopped'
        status = self.container.status
        status_map = {
            'created': 'starting',
            'restarting': 'running',
            'running': 'running',
            'removing': 'running',
            'paused': 'running',
            'exited': 'success',
            'dead': 'failed'
        }
        if status in status_map:
            return status_map[status]

        return 'unknown'
