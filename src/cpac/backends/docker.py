import docker

from cpac.backends.platform import Backend


class Docker(Backend):
    def __init__(self, **kwargs):
        print("Loading 🐳 Docker")
        self.client = docker.from_env()
        try:
            self.client.ping()
        except docker.errors.APIError:  # pragma: no cover
            raise OSError("Could not connect to Docker")
        self.volumes = {}
        self._set_bindings(**kwargs)
        self.docker_kwargs = {}
        if isinstance(kwargs['container_options'], list):
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

    def _load_logging(self, image):
        import pandas as pd
        import textwrap
        from tabulate import tabulate

        t = pd.DataFrame([
            (i, j['bind'], j['mode']) for i in self.bindings['volumes'].keys(
            ) for j in self.bindings['volumes'][i]
        ])
        t.columns = ['local', 'Docker', 'mode']
        print(" ".join([
            "Loading 🐳",
            image,
            "with these directory bindings:"
        ]))
        print(textwrap.indent(
            tabulate(t, headers='keys', showindex=False),
            '  '
        ))
        print("Logging messages will refer to the Docker paths.\n")

    def run(self, flags="", **kwargs):
        kwargs['command'] = [i for i in [
            kwargs['bids_dir'],
            kwargs['output_dir'],
            kwargs['level_of_analysis'],
            *flags.split(' ')
        ] if (i is not None and len(i))]
        self._execute(**kwargs)

    def utils(self, flags="", **kwargs):
        kwargs['command'] = [i for i in [
            kwargs.get('bids_dir', kwargs.get('working_dir', '/tmp')),
            kwargs.get('output_dir', '/outputs'),
            'cli',
            '--',
            'utils',
            *flags.split(' ')
        ] if (i is not None and len(i))]
        self._execute(**kwargs)

    def _execute(self, command, **kwargs):
        image = ':'.join([
            kwargs['image'] if kwargs.get(
                'image'
            ) is not None else 'fcpindi/c-pac',
            self.bindings['tag'] if self.bindings.get(
                'tag'
            ) is not None else 'latest'
        ])

        self._load_logging(image)

        self._run = DockerRun(self.client.containers.run(
            image,
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
