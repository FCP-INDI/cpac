"""Base classes for platform-specific implementations."""
import atexit
from collections import namedtuple
from contextlib import redirect_stderr
from io import StringIO
import os
import pwd
import tempfile
import textwrap
from typing import overload
from warnings import warn

from docker import errors as docker_errors
import pandas as pd
from tabulate import tabulate
import yaml

from cpac import __version__ as cpac_version
from cpac.helpers import cpac_read_crash, get_extra_arg_value
from cpac.helpers.cpac_parse_resources import get_or_create_config
from cpac.utils import LocalsToBind, Volume, Volumes


class CpacVersion:
    """Class to hold the version of C-PAC running in the container."""

    # pylint: disable=too-few-public-methods
    def __init__(self, backend):
        self.versions = namedtuple("versions", "cpac CPAC")
        self.versions.cpac = cpac_version
        self.versions.CPAC = backend.get_response("cat /code/version").rstrip()
        self.platform = backend.platform

    def __str__(self):
        return (
            f"cpac (convenience wrapper) version {self.versions.cpac}\n"
            f"C-PAC version {self.versions.CPAC} running on "
            f"{self.platform.name} version {self.platform.version}"
        )


class _MockBinding:
    """Class to hold a ``.bind`` property with the value ``None``."""

    def __init__(self):
        self.bind = None

    def __bool__(self):
        return False

    def __repr__(self):
        return "cpac.backends.platform._MockBinding()"

    def __str__(self):
        return "None"


class PlatformMeta:
    """Class to hold platform metadata."""

    # pylint: disable=too-few-public-methods
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol
        self.version = "unknown"

    def __str__(self):
        return f"{self.symbol} {self.name}"


class Backend:
    def __init__(self, **kwargs):
        self.pipeline_config = None
        if "extra_args" in kwargs and isinstance(kwargs["extra_args"], list):
            pipeline_config = get_extra_arg_value(kwargs["extra_args"], "pipeline_file")
            if pipeline_config is not None:
                self.pipeline_config = yaml.safe_load(pipeline_config)
            else:
                pipeline_config = get_extra_arg_value(kwargs["extra_args"], "preconfig")
                if pipeline_config is not None:
                    self.pipeline_config = "/".join(
                        [
                            "/code/CPAC/resources/configs",
                            f"pipeline_config_{pipeline_config}.yml",
                        ]
                    )
        self.volumes = Volume("/etc/passwd", mode="ro")
        tracking_opt_out = "--tracking_opt-out"
        if not (
            tracking_opt_out in kwargs
            or tracking_opt_out in kwargs.get("extra_args", [])
        ):
            udir = os.path.expanduser("~")
            if udir != "/":
                tracking_path = get_or_create_config(udir)
                self.volumes += Volume(tracking_path)
            else:
                raise EnvironmentError(
                    "Unable to create tracking "
                    "configuration. Please run with "
                    "--tracking_opt-out and C-PAC >= "
                    "1.8.4"
                )
        # initilizing these for overriding on load
        self.bindings = {}
        self.container = None
        self.image = None
        self.platform = None
        self._run = None
        self.uid = 0
        self.username = "root"
        self.working_dir = kwargs.get("working_dir", os.getcwd())
        atexit.register(self._cleanup)

    def __del__(self):
        self._cleanup()

    def read_crash(self, crashfile, flags=None, **kwargs):
        """
        Decode a crashfile into plain text.

        For C-PAC < 1.8.0. Since C-PAC 1.8.0, crashfiles are stored as plain text.

        Parameters
        ----------
        crashfile : str
            Path to the crashfile to decode.

        flags : list

        Returns
        -------
        None
        """
        if flags is None:
            flags = []
        os.chmod(cpac_read_crash.__file__, 0o775)
        self._set_crashfile_binding(crashfile)
        if self.platform.name == "Singularity":
            self._load_logging()
        stderr = StringIO()
        with redirect_stderr(stderr):
            del kwargs["command"]
            crash_lines = list(
                self._read_crash(f"{cpac_read_crash.__file__} {crashfile}", **kwargs)
            )
            crash_message = "".join(
                [
                    crash_line.decode("utf-8")
                    if isinstance(crash_line, bytes)
                    else crash_line
                    for crash_line in (
                        [line[0] for line in crash_lines]
                        if (len(crash_lines) and isinstance(crash_lines[0], tuple))
                        else crash_lines
                    )
                ]
            )
            crash_message += stderr.getvalue()
            stderr.read()  # clear stderr
            print(crash_message.strip())

    def _bind_volume(self, volume: Volume) -> None:
        """Binds a volume to the container.

        Parameters
        ----------
        volume : Volume
            Volume to bind.
        """
        self.volumes += self._prep_binding(volume)

    def _collect_config_binding(self, config, config_key):
        config_binding = _MockBinding()
        if isinstance(config, str):
            if os.path.exists(config):
                self._set_bindings(custom_binding=Volume(config, mode="r"))
                config = self.clarg(
                    clcommand='python -c "from CPAC.utils.configuration; '
                    "import Configuration; "
                    f'yaml.dump(Configuration({config}).dict())"'
                )
            config = yaml.safe_load(config)
        if config:
            pipeline_setup = config.get("pipeline_setup", {})
            minimal = pipeline_setup.get("FROM", False)
            if isinstance(pipeline_setup, dict):
                config_binding = Volume(pipeline_setup.get(config_key, {}).get("path"))
            else:
                minimal = True
            if minimal:
                warn(
                    "This run is using a minimal pipeline configuration. If "
                    "this configuration imports a configuration that "
                    "requires paths to be bound from your real environment "
                    "to your container, you need to bind those paths "
                    "manually with the `-B` flag.",
                    UserWarning,
                )
        return config_binding

    def clarg(self, clcommand, flags=None, **kwargs):
        """Run a commandline command.

        Parameters
        ----------
        clcommand: str

        flags: list, optional

        kwargs: dict
        """
        raise NotImplementedError

    def _cleanup(self):
        if hasattr(self, "container") and hasattr(self.container, "stop"):
            try:
                self.container.stop()
            except (docker_errors.APIError, docker_errors.NotFound):
                pass

    def collect_config_bindings(self, config, **kwargs):
        """Collect bindings for a given configuration.

        Parameters
        ----------
        config : str or dict
            Configuration to collect bindings for.

        kwargs : dict
            Extra arguments from the commandline.

        kwargs['output_dir'] : str
            Output directory for the run.

        kwargs['working_dir'] : str
            Working directory for the run.

        Returns
        -------
        kwargs : dict
        """
        kwargs["output_dir"] = kwargs.get("output_dir", os.getcwd())
        kwargs["working_dir"] = self.working_dir

        config_bindings = Volumes()
        cwd = os.getcwd()
        for c_b in (
            ("log_directory", "log"),
            ("working_directory", "working", "working_dir"),
            ("crash_log_directory", "log"),
            ("output_directory", "outputs", "output_dir"),
        ):
            inner_binding = self._collect_config_binding(config, c_b[0]).bind
            outer_binding = None
            if inner_binding is not None:
                if len(c_b) == 3:  # noqa: PLR2004
                    if kwargs.get(c_b[2]) is not None:
                        outer_binding = kwargs[c_b[2]]
                    else:
                        kwargs[c_b[2]] = inner_binding
                try:
                    os.makedirs(inner_binding, exist_ok=True)
                except (PermissionError, OSError):
                    outer_binding = os.path.join(
                        kwargs.get("output_dir", os.path.join(cwd, "outputs")), c_b[1]
                    )
                if outer_binding is not None and inner_binding is not None:
                    config_bindings += Volume(inner_binding)
                elif outer_binding is not None:
                    config_bindings += Volume(outer_binding)
            else:
                path = os.path.join(cwd, c_b[1])
                config_bindings += Volume(path)
        kwargs["config_bindings"] = config_bindings
        return kwargs

    def get_response(self, command, **kwargs):
        """
        Return the response of running a command in the container.

        Implemented in the subclasses.

        Parameters
        ----------
        command : str

        Returns
        -------
        str
        """
        raise NotImplementedError

    def get_version(self):
        """Get the version of C-PAC running in container.

        Parameters
        ----------
        None

        Returns
        -------
        CpacVersion
        """
        version = CpacVersion(self)
        print(version)
        return version

    def _load_logging(self):
        table = pd.DataFrame(
            [
                (volume.local, volume.bind, volume.mode)
                for volume in self.bindings["volumes"]
            ]
        )
        if not table.empty:
            table.columns = ["local", self.platform.name, "mode"]
            self._print_loading_with_symbol(
                " ".join(
                    [
                        self.image,
                        f'as "{self.username} ({self.uid})"',
                        "with these directory bindings:",
                    ]
                )
            )
            print(
                textwrap.indent(
                    tabulate(
                        table.applymap(
                            lambda x: ("\n".join(textwrap.wrap(x, 42)))
                            if isinstance(x, str)
                            else x
                        ),
                        headers="keys",
                        showindex=False,
                    ),
                    "  ",
                )
            )
            print(
                f"Logging messages will refer to the {self.platform.name} " "paths.\n"
            )

    def _prep_binding(self, volume: Volume, second_try: bool = False) -> Volume:
        """Prepare a volume binding for the container.

        Parameters
        ----------
        volume : Volume
            Volume to bind.

        second_try : bool
            Whether this is a second try to bind the volume.

        Returns
        -------
        Volume
        """
        volume.local = os.path.abspath(os.path.expanduser(volume.local))
        if not os.path.exists(volume.local):
            try:
                os.makedirs(volume.local, exist_ok=True)
            except (PermissionError, OSError) as perm:
                if second_try:
                    raise perm
                new_local = os.path.join(self.working_dir, volume.local.lstrip("/"))
                print(
                    f"Could not create {volume.local}. Binding "
                    f"{volume.bind} to {new_local} instead."
                )
                volume.local = new_local
                return self._prep_binding(volume, second_try=True)
        return volume

    def _print_loading_with_symbol(self, message, prefix="Loading"):
        if prefix is not None:
            print(prefix, end=" ")
        try:
            print(" ".join([self.platform.symbol, message]))
        except UnicodeEncodeError:
            print(message)

    @overload
    def __setattr__(self, name: str, value: Volume) -> None:
        ...

    @overload
    def __setattr__(self, name: str, value: list) -> None:
        ...

    @overload
    def __setattr__(self, name: str, value: Volumes) -> None:
        ...

    def __setattr__(self, name, value):
        if name == "volumes":
            if isinstance(value, Volumes):
                self.__dict__[name] = value
            else:
                self.__dict__[name] = Volumes(value)
        else:
            self.__dict__[name] = value

    def _set_bindings(self, **kwargs):
        tag = kwargs.get("tag", None)
        tag = tag if isinstance(tag, str) else None

        for kwarg in [*kwargs.get("extra_args", []), kwargs.get("crashfile", "")]:
            if os.path.exists(kwarg):
                self._bind_volume(Volume(kwarg, mode="r"))
        if (
            "data_config_file" in kwargs
            and isinstance(kwargs["data_config_file"], str)
            and os.path.exists(kwargs["data_config_file"])
        ):
            self._bind_volume(Volume(kwargs["data_config_file"], mode="r"))
            locals_from_data_config = LocalsToBind()
            locals_from_data_config.from_config_file(kwargs["data_config_file"])
            for local in locals_from_data_config.locals:
                self._bind_volume(Volume(local, mode="r"))
        for dir_type in ["working", "output"]:
            self._bind_volume(Volume(kwargs[f"{dir_type}_dir"]))
        if kwargs.get("custom_binding"):
            for d in kwargs["custom_binding"]:  # pylint: disable=invalid-name
                bind_parts = d.split(":")
                if len(bind_parts) == 3:  # noqa: PLR2004
                    self._bind_volume(Volume(*bind_parts))
                elif len(bind_parts) == 2:  # noqa: PLR2004
                    self._bind_volume(Volume(*bind_parts, mode="rw"))
                elif len(bind_parts) == 1:  # noqa: PLR2004, RUF100
                    self._bind_volume(Volume(bind_parts[0]))
                else:
                    raise SyntaxError(
                        "I don't know what to do with custom " "binding {}".format(d)
                    )
        for d in ["bids_dir", "output_dir"]:  # pylint: disable=invalid-name
            if d in kwargs and isinstance(kwargs[d], str) and os.path.exists(kwargs[d]):
                self._bind_volume(
                    Volume(kwargs[d], mode="rw" if d == "output_dir" else "r")
                )
        if kwargs.get("config_bindings"):
            for binding in kwargs["config_bindings"]:
                self._bind_volume(binding)
        self.uid = os.getuid()
        pwuid = pwd.getpwuid(self.uid)
        self.username = getattr(
            pwuid, "pw_name", getattr(pwuid, "pw_gecos", str(self.uid))
        )
        self.bindings.update({"tag": tag, "uid": self.uid, "volumes": self.volumes})

    def _volumes_to_docker_mounts(self):
        return {"volumes": [str(volume) for volume in self.volumes]}

    def _set_crashfile_binding(self, crashfile):
        for ckey in ["/wd/", "/crash/", "/log"]:
            if ckey in crashfile:
                self._bind_volume(Volume(crashfile.split(ckey)[0], "/outputs", "rw"))
        with tempfile.TemporaryDirectory() as temp_dir:
            self._bind_volume(Volume(temp_dir, "/out", "rw"))
        helper = cpac_read_crash.__file__
        self._bind_volume(Volume(helper, mode="ro"))


class Result:
    mime = None

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __call__(self):
        yield self.value

    @property
    def description(self):
        return {"type": "object"}


class FileResult(Result):
    def __init__(self, name, value, mime):
        self.name = name
        self.value = value
        self.mime = mime

    def __call__(self):
        with open(self.value, "rb") as f:
            while True:
                piece = f.read(1024)
                if piece:
                    yield piece
                else:
                    return

    @property
    def description(self):
        return {"type": "file", "mime": self.mime}
