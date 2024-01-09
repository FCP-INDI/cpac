from __future__ import annotations

from itertools import permutations
import os
from typing import ClassVar, Iterator, Optional, Set, Union
from warnings import warn

import yaml

from cpac import DIST_NAME


class LocalsToBind:
    """Class to collect local directories to bind to containers."""

    def __init__(self):
        self.locals = set()

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.locals)

    def from_config_file(self, config_path):
        """
        Add local bindings from a configuration file.

        Paramter.
        --------
        config_path : str
            path to data config file
        """
        with open(config_path, "r") as config_yml:
            config_dict = yaml.safe_load(config_yml)
        self._add_locals(config_dict)

    def _add_locals(self, local: str) -> None:
        """
        Add local paths to bindings.

        Parameter.
        ---------
        local : any
            object to search for local paths
        """
        # pylint: disable=expression-not-assigned
        if isinstance(local, dict):
            for k in local:
                self._add_locals(local[k])
        elif isinstance(local, (list, tuple)):
            for i in local:
                self._add_locals(i)
        elif isinstance(local, str):
            if os.path.exists(local):
                self.locals.add(local)
        self._local_common_paths()

    def _local_common_paths(self):
        new_locals = set()
        stragglers = set()

        def common_path(paths):
            x = os.path.commonprefix(list(paths))
            while not x.endswith("/"):
                x = x[:-2]
            x
            return x

        for i in list(permutations(self.locals, 3)):
            c = common_path(i)
            if len(c) > 1:
                new_locals.add(c)
            else:
                for f in i:
                    stragglers.add(f)
        self.locals = new_locals | {
            s for s in stragglers if not any(s.startswith(n) for n in new_locals)
        }


class PermissionMode:
    """
    Class to overload comparison operators to compare file permissions levels.

    'rw' > 'w' > 'r'

    Examples
    --------
    >>> PermissionMode('ro') > PermissionMode('rw')
    False
    >>> PermissionMode('rw') > PermissionMode('r')
    True
    >>> PermissionMode('r') > PermissionMode('r')
    False
    >>> PermissionMode('ro') >= PermissionMode('rw')
    False
    >>> PermissionMode('rw') >= PermissionMode('r')
    True
    >>> PermissionMode('r') >= PermissionMode('r')
    True
    >>> PermissionMode('ro') < PermissionMode('rw')
    True
    >>> PermissionMode('rw') < PermissionMode('r')
    False
    >>> PermissionMode('r') < PermissionMode('r')
    False
    >>> PermissionMode('ro') <= PermissionMode('rw')
    True
    >>> PermissionMode('ro') <= PermissionMode('ro')
    True
    >>> PermissionMode('rw') <= PermissionMode('ro')
    False
    >>> PermissionMode('ro') == PermissionMode('rw')
    False
    >>> PermissionMode('ro') == PermissionMode('r')
    True
    """

    defined_modes: ClassVar[Set[str]] = {"rw", "w", "r", "ro"}

    def __init__(self, fs_str):
        self.mode = (
            fs_str.mode
            if isinstance(fs_str, PermissionMode)
            else "ro"
            if fs_str == "r"
            else fs_str
        )
        self.defined = self.mode in PermissionMode.defined_modes
        self._warn_if_undefined()

    def __repr__(self):
        return self.mode

    def __eq__(self, other):
        return self.mode == other.mode

    def __gt__(self, other):
        for permission in (self, other):
            if permission._warn_if_undefined():
                return NotImplemented
        if self.mode == "rw":
            if other.mode in {"w", "ro"}:
                return True
        elif self.mode == "w" and other.mode == "ro":
            return True
        return False

    def __ge__(self, other):
        for permission in (self, other):
            if permission._warn_if_undefined():
                return NotImplemented
        if self.mode == other.mode or self > other:
            return True
        return False

    def __lt__(self, other):
        for permission in (self, other):
            if permission._warn_if_undefined():
                return NotImplemented
        if self.mode == "ro":
            if other.mode in {"w", "rw"}:
                return True
        elif self.mode == "ro" and other.mode == "w":
            return True
        return False

    def __le__(self, other):
        for permission in (self, other):
            if permission._warn_if_undefined():
                return NotImplemented
        if self.mode == other.mode or self < other:
            return True
        return False

    def _warn_if_undefined(self):
        if not self.defined:
            warn(
                f"'{self.mode}' is not a fully-configured permission "
                f"level in {DIST_NAME}. Configured permission levels are "
                f"""{", ".join([
                     f"'{mode}'" for mode in PermissionMode.defined_modes
                 ])}""",
                UserWarning,
            )
            return True
        return False


class Volume:
    """Class to store bind volume information."""

    def __init__(
        self,
        local: str,
        bind: Optional[str] = None,
        mode: Optional[Union[str, PermissionMode]] = None,
    ) -> None:
        self.local = local
        self.bind = bind if bind is not None else local
        if self.bind is not None and not self.bind.startswith("/"):
            self.bind = os.path.abspath(self.bind)
        if isinstance(mode, PermissionMode):
            self.mode = mode
        elif mode is not None:
            self.mode = PermissionMode(mode)
        else:
            self.mode = PermissionMode("rw")

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{self.local}:{self.bind}:{self.mode}"


class Volumes:
    """Class to store all bind volumes. Prevents duplicate mount points."""

    def __init__(self, volumes: Optional[Union[list, Volume]] = None) -> None:
        try:
            if volumes is None:
                self.volumes = {}
            elif isinstance(volumes, list):
                self.volumes = {
                    volume.local: volume
                    for volume in [Volume(volume) for volume in volumes]
                }
            elif isinstance(volumes, Volume):
                self.volumes = {volumes.local: volumes}
        except AttributeError as attribute_error:
            raise TypeError(
                "Volumes must be initialized with a Volume "
                "object, a list of Volume objects or None"
            ) from attribute_error

    def __add__(self, other: Union[list, Volume, Volumes]) -> Volumes:
        """Add volume.

        Parameters
        ----------
        other : Volume, list, or Volumes
            Volume(s) to add

        Returns
        -------
        Volumes
        """
        new_volumes = Volumes([self.volumes.copy()])
        if isinstance(other, (list, Volumes)):
            for volume in other:
                new_volumes += volume
        elif isinstance(other, Volume):
            new_volumes.volumes.update({other.bind: other})
        return new_volumes

    def __iadd__(self, other: Union[list, Volume, Volumes]) -> Volumes:
        """Add volume in place.

        Parameters
        ----------
        other : Volume, list, or Volumes
            Volume(s) to add

        Returns
        -------
        Volumes
        """
        if isinstance(other, (list, Volumes)):
            for volume in other:
                self += volume
        elif isinstance(other, Volume):
            self.volumes.update({other.bind: other})
        return self

    def __isub__(self, bind: str) -> Volumes:
        """Remove volume in place.

        Parameters
        ----------
        bind : str
            key of Volume to remove

        Returns
        -------
        Volumes
        """
        if bind in self.volumes:
            del self.volumes[bind]
        return self

    def __iter__(self) -> Iterator[Volume]:
        """Iterate over volumes."""
        return iter(self.volumes.values())

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return str(list(self.volumes.values()))

    def __sub__(self, bind: str) -> Volumes:
        """Remove volume.

        Parameters
        ----------
        bind : str
            key of Volume to remove

        Returns
        -------
        Volumes
        """
        new_volumes = Volumes([self.volumes.copy()])
        if bind in new_volumes.volumes:
            del new_volumes.volumes[bind]
        return new_volumes
