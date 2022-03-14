import os
import yaml

from cpac import dist_name
from itertools import permutations
from warnings import warn


class Locals_to_bind():
    """
    Class to collect local directories to bind to containers.
    """
    def __init__(self):
        self.locals = set()

    def __repr__(self):
        return(str(self.locals))

    def from_config_file(self, config_path):
        """
        Paramter
        --------
        config_path: str
            path to data config file
        """
        with open(config_path, 'r') as r:
            config_dict = yaml.safe_load(r)
        self._add_locals(config_dict)

    def _add_locals(self, d):
        """
        Parameter
        ---------
        d: any
            object to search for local paths
        """
        # pylint: disable=expression-not-assigned
        if isinstance(d, dict):
            [self._add_locals(d[k]) for k in d]
        elif isinstance(d, (list, tuple)):
            [self._add_locals(i) for i in d]
        elif isinstance(d, str):
            if os.path.exists(d):
                self.locals.add(d)
        self._local_common_paths()

    def _local_common_paths(self):
        new_locals = set()
        stragglers = set()

        def common_path(paths):
            x = os.path.commonprefix(list(paths))
            while not x.endswith('/'):
                x = x[:-2]
            x
            return(x)
        for i in list(permutations(self.locals, 3)):
            c = common_path(i)
            if len(c) > 1:
                new_locals.add(c)
            else:
                for f in i:
                    stragglers.add(f)
        self.locals = new_locals | {s for s in stragglers if not any([
            s.startswith(n) for n in new_locals
        ])}


class PermissionMode():
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
    defined_modes = {'rw', 'w', 'r', 'ro'}

    def __init__(self, fs_str):

        self.mode = fs_str.mode if isinstance(
            fs_str,
            PermissionMode
        ) else 'ro' if fs_str == 'r' else fs_str
        self.defined = self.mode in PermissionMode.defined_modes
        self._warn_if_undefined()

    def __repr__(self):
        return(self.mode)

    def __eq__(self, other):
        for permission in (self, other):
            return self.mode == other.mode

    def __gt__(self, other):
        for permission in (self, other):
            if(permission._warn_if_undefined()):  # pragma: no cover
                return(NotImplemented)

        if self.mode == 'rw':
            if other.mode in {'w', 'ro'}:
                return(True)
        elif self.mode == 'w' and other.mode == 'ro':
            return(True)

        return(False)

    def __ge__(self, other):
        for permission in (self, other):
            if(permission._warn_if_undefined()):  # pragma: no cover
                return(NotImplemented)

        if self.mode == other.mode or self > other:
            return(True)

        return(False)

    def __lt__(self, other):
        for permission in (self, other):
            if(permission._warn_if_undefined()):  # pragma: no cover
                return(NotImplemented)

        if self.mode == 'ro':
            if other.mode in {'w', 'rw'}:
                return(True)
        elif self.mode == 'ro' and other.mode == 'w':
            return(True)

        return(False)

    def __le__(self, other):
        for permission in (self, other):
            if(permission._warn_if_undefined()):  # pragma: no cover
                return(NotImplemented)

        if self.mode == other.mode or self < other:
            return(True)

        return(False)

    def _warn_if_undefined(self):  # pragma: no cover
        if not self.defined:
            warn(
                f'\'{self.mode}\' is not a fully-configured permission '
                f'level in {dist_name}. Configured permission levels are '
                f'''{", ".join([
                    f"'{mode}'" for mode in PermissionMode.defined_modes
                ])}''',
                UserWarning
            )
            return(True)
        return(False)


def ls_newest(directory, extensions):
    """
    Function to return the most-recently-modified of a given extension in a
    given directory

    Parameters
    ----------
    directory: str

    extension: iterable

    Returns
    -------
    full_path_to_file: str or None if none found
    """
    ls = [
        os.path.join(
            directory,
            d
        ) for d in os.listdir(
            directory
        ) if any([d.endswith(
            extension.lstrip('.').lower()
        ) for extension in extensions])
    ]
    ls.sort(key=lambda fp: os.stat(fp).st_mtime)
    try:
        return(ls[-1])
    except IndexError:  # pragma: no cover
        return(None)
