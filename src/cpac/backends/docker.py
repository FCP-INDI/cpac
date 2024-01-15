import os

import docker
from docker.errors import ImageNotFound
import dockerpty

from cpac.backends.platform import Backend, PlatformMeta


class Docker(Backend):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container = None
        self.platform = PlatformMeta("Docker", "🐳")
        self._print_loading_with_symbol(self.platform.name)
        self.client = docker.from_env()
        self.platform.version = self.client.version().get("Version", "unknown")
        try:
            self.client.ping()
        except (docker.errors.APIError, ConnectionError):  # pragma: no cover
            raise OSError(
                f"Could not connect to {self.platform.name}. " "Is Docker running?"
            )

        image = kwargs["image"] if kwargs.get("image") is not None else "fcpindi/c-pac"

        tag = kwargs["tag"] if kwargs.get("tag") is not None else "latest"
        self.image = ":".join([image, tag])

        self._collect_config(**kwargs)
        self.docker_kwargs = {"init": True}
        if isinstance(kwargs.get("container_options"), list):
            for opt in kwargs["container_options"]:
                if "=" in opt or " " in opt:
                    delimiter = min(
                        [i for i in [opt.find("="), opt.find(" ")] if i > 0]
                    )
                    k = opt[:delimiter].lstrip("-").replace("-", "_")
                    v = opt[delimiter + 1 :].strip('"').strip("'")
                    if k in self.docker_kwargs:
                        if isinstance(self.docker_kwargs[k], list):
                            self.docker_kwargs[k].append(v)
                        else:
                            self.docker_kwargs[k] = [self.docker_kwargs[k], v]
                    else:
                        self.docker_kwargs[k] = v

    def _collect_config(self, **kwargs):
        if kwargs.get("command") not in {"pull", "upgrade", None}:
            if isinstance(self.pipeline_config, str):
                container_kwargs = {"image": self.image}
                if os.path.exists(self.pipeline_config):
                    container_kwargs["volumes"] = {
                        self.pipeline_config: {
                            "bind": self.pipeline_config,
                            "mode": "ro",
                        }
                    }
                try:
                    container = self.client.containers.create(**container_kwargs)
                except ImageNotFound:  # pragma: no cover
                    self.pull(**kwargs)
                    container = self.client.containers.create(**container_kwargs)
                stream = container.get_archive(path=self.pipeline_config)[0]
                self.config = (
                    b"".join(list(stream))
                    .split(b"\x000000000")[-1]
                    .replace(b"\x00", b"")
                    .decode()
                )
                container.remove()
            else:
                self.config = self.pipeline_config
            kwargs = self.collect_config_bindings(self.config, **kwargs)
            self._set_bindings(**kwargs)

    def pull(self, **kwargs):
        image, tag = self.image.split(":")
        [
            print(layer[k])
            for layer in self.client.api.pull(
                repository=image, tag=tag, stream=True, decode=True
            )
            for k in layer
            if k in {"id", "status", "progress"}
        ]

    def _read_crash(self, read_crash_command, **kwargs):
        return self._execute(command=read_crash_command, run_type="exec", **kwargs)

    def run(self, flags=[], **kwargs):
        kwargs["command"] = [
            i
            for i in [
                kwargs.get("bids_dir"),
                kwargs.get("output_dir"),
                kwargs.get("level_of_analysis"),
                *flags,
            ]
            if (i is not None and len(i))
        ]
        return self._execute(**kwargs)

    def clarg(self, clcommand, flags=None, **kwargs):
        """Run a commandline command.

        Parameters
        ----------
        clcommand: str

        flags: list or None

        kwargs: dict
        """
        if flags is None:
            flags = []
        kwargs["command"] = [
            i
            for i in [
                kwargs.get("bids_dir", kwargs.get("working_dir", "/tmp")),
                kwargs.get("output_dir", "/outputs"),
                "cli",
                "--",
                clcommand,
                *flags,
            ]
            if (i is not None and len(i))
        ]
        self._execute(**kwargs)

    def _execute(self, command, run_type="run", **kwargs):
        container_return = None
        try:
            self.client.images.get(self.image)
        except docker.errors.ImageNotFound:  # pragma: no cover
            self.pull(**kwargs)

        if run_type != "version":
            self._load_logging()

        shared_kwargs = {
            "image": self.image,
            "user": str(self.bindings["uid"]),
            **self._volumes_to_docker_mounts(),
            "working_dir": kwargs.get("working_dir", os.getcwd()),
            **self.docker_kwargs,
        }

        if run_type == "run":
            self.container = self.client.containers.run(
                **shared_kwargs,
                command=command,
                detach=True,
                stderr=True,
                stdout=True,
                remove=True,
            )
            self._run = DockerRun(self.container)
        elif run_type == "version":
            return self.get_version()
        elif run_type == "exec":
            self.container = self.client.containers.create(
                **shared_kwargs,
                auto_remove=True,
                entrypoint="/bin/bash",
                stdin_open=True,
            )
            self.container.start()
            container_return = self.container.exec_run(
                cmd=command, stdout=True, stderr=True, stream=True
            )[1]
        elif run_type == "enter":
            self.container = self.client.containers.create(
                **shared_kwargs,
                auto_remove=True,
                entrypoint="/bin/bash",
                stdin_open=True,
                tty=True,
                detach=False,
            )
            dockerpty.start(self.client.api, self.container.id)
        return container_return

    def get_response(self, command, **kwargs):
        """
        Return the response of running a command in the Docker container.

        Parameters
        ----------
        command : str

        Returns
        -------
        str
        """
        full_response = []
        for response in self._execute(command, run_type="exec", **kwargs):
            full_response.append(response.decode())
        return "".join(full_response)


class DockerRun:
    def __init__(self, container):
        # pylint: disable=expression-not-assigned
        self.container = container
        [
            print(l.decode("utf-8"), end="")
            for l in self.container.attach(  # noqa E741
                logs=True, stderr=True, stdout=True, stream=True
            )
        ]

    @property
    def status(self):
        try:
            self.container.reload()
        except Exception:
            return "stopped"
        status = self.container.status
        status_map = {
            "created": "starting",
            "restarting": "running",
            "running": "running",
            "removing": "running",
            "paused": "running",
            "exited": "success",
            "dead": "failed",
        }
        if status in status_map:
            return status_map[status]

        return "unknown"
