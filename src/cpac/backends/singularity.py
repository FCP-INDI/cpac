from itertools import chain
import os

from spython.image import Image
from spython.main import Client

from cpac.backends.platform import Backend, PlatformMeta

BINDING_MODES = {"ro": "ro", "w": "rw", "rw": "rw"}


class Singularity(Backend):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container = None
        self.platform = PlatformMeta("Singularity", "Ⓢ")
        self.platform.version = Client.version().split(" ")[-1]
        self._print_loading_with_symbol(self.platform.name)
        self.pull(**kwargs, force=False)
        self.options = (
            list(chain.from_iterable(kwargs["container_options"]))
            if bool(kwargs.get("container_options"))
            else []
        )
        if isinstance(self.pipeline_config, str):
            self.config = Client.execute(
                image=self.image,
                command=f"cat {self.pipeline_config}",
                return_result=False,
            )
        else:
            self.config = self.pipeline_config
        kwargs = self.collect_config_bindings(self.config, **kwargs)
        del self.config
        self._set_bindings(**kwargs)

    def _bindings_as_option(self):
        self.options += [
            "-B",
            ",".join(
                [
                    ":".join([binding.local, binding.bind, str(binding.mode)])
                    for binding in self.volumes
                ]
            ),
        ]

    def _bindings_from_option(self):
        enter_options = {}
        if "-B" in self.options:
            enter_options["bind"] = self.options[self.options.index("-B") + 1]
            self.options.remove(enter_options["bind"])
            self.options.remove("-B")
        enter_options["singularity_options"] = self.options
        return enter_options

    def _pull(self, img, force, pull_folder):
        """Try to pull image gracefully."""
        try:
            self.image = Client.pull(img, force=force, pull_folder=pull_folder)
        except ValueError as value_error:
            if "closed file" in str(value_error):
                # pylint: disable=protected-access
                self.image = Image(Client._get_filename(img))

    def pull(self, force=False, **kwargs):
        image = kwargs["image"] if kwargs.get("image") is not None else "fcpindi/c-pac"
        tag = kwargs.get("tag")
        pwd = os.getcwd()
        if kwargs.get("working_dir") is not None:
            pwd = kwargs["working_dir"]
            os.chdir(pwd)
        image_path = Client._get_filename(  # pylint: disable=protected-access
            image if tag is None else ":".join([image, tag])
        )
        if (
            not force
            and image
            and isinstance(image, str)
            and os.path.exists(image_path)
        ):
            self.image = image_path
        elif tag and isinstance(tag, str):  # pragma: no cover
            self._pull(f"docker://{image}:{tag}", force=force, pull_folder=pwd)
        else:  # pragma: no cover
            try:
                self._pull(
                    "docker://fcpindi/c-pac:latest", force=force, pull_folder=pwd
                )
            except Exception as exception:
                raise OSError("Could not connect to Singularity") from exception

    def get_response(self, command, **kwargs):
        """
        Return the response of running a command in the Singularity container.

        Parameters
        ----------
        command : str

        Returns
        -------
        str
        """
        full_response = []
        for response in self._try_to_stream(
            args={"command": command}, stream_command="execute", silent=True, **kwargs
        ):
            full_response.append(response)
        return "".join(full_response)

    def _try_to_stream(self, args, stream_command="run", silent=False, **kwargs):
        self._bindings_as_option()
        if stream_command == "run":
            self.container = Client.run(
                Client.instance(self.image),
                args=args,
                options=self.options,
                stream=not silent,
                return_result=True,
                **kwargs,
            )
        else:
            enter_options = self._bindings_from_option()
            if stream_command == "execute":
                self.container = Client.execute(
                    self.image,
                    command=args["command"].split(" "),
                    options=self.options,
                    stream=not silent,
                    quiet=silent,
                    **{
                        kwarg: value
                        for kwarg, value in kwargs.items()
                        if kwarg
                        in [
                            "contain",
                            "environ",
                            "nv",
                            "sudo",
                            "return_result",
                            "writable",
                        ]
                    },
                )
            elif stream_command == "enter":
                Client.shell(self.image, **enter_options, **kwargs)
        if self.container is not None:
            for line in self.container:
                yield line
            if hasattr(self.container, "close") and callable(self.container.close):
                self.container.close()

    def _read_crash(self, read_crash_command, **kwargs):
        return self._try_to_stream(
            args={"command": read_crash_command}, stream_command="execute", **kwargs
        )

    def run(self, flags=None, run_type="run", **kwargs):
        # pylint: disable=expression-not-assigned
        if flags is None:
            flags = []
        self._load_logging()
        if run_type == "run":
            [
                print(o, end="")
                for o in self._try_to_stream(
                    args=" ".join(
                        [
                            kwargs["bids_dir"],
                            kwargs["output_dir"],
                            kwargs["level_of_analysis"],
                            *flags,
                        ]
                    ).strip(" ")
                )
            ]
        elif run_type == "version":
            return self.get_version()
        else:
            for o in self._try_to_stream(
                args=" ".join(flags).strip(" "), stream_command=run_type
            ):
                print(o, end="")
        return None

    def clarg(self, clcommand, flags=None, **kwargs):
        """
        Run a commandline command.

        Parameters
        ----------
        clcommand: str

        flags: list

        kwargs: dict
        """
        # pylint: disable=expression-not-assigned
        if flags is None:
            flags = []
        self._load_logging()
        [
            print(o, end="")
            for o in self._try_to_stream(
                args=" ".join(
                    [
                        kwargs.get("bids_dir", "bids_dir"),
                        kwargs.get("output_dir", "output_dir"),
                        f"cli -- {clcommand}",
                        *flags,
                    ]
                ).strip(" ")
            )
        ]
