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
        if isinstance(d, dict):
            [self._add_locals(d[k]) for k in d]
        elif isinstance(d, list) or isinstance(d, tuple):
            [self._add_locals(i) for i in d]
        elif isinstance(d, str):
            if os.path.exists(d):
                if os.path.isdir(d):
                    self.locals.add(d)
                else:
                    self.locals.add(os.path.dirname(d))
        self._local_common_paths()

    def _local_common_paths(self):
        new_locals = set()
        stragglers = set()
        for i in list(permutations(self.locals, 3)):
            c = common_path(i)
            if len(c)>1:
                new_locals.add(c)
            else:
                for f in i:
                    stragglers.add(f)
        self.locals = new_locals | {s for s in stragglers if not any([
            s.startswith(n) for n in new_locals
        ])}

        def common_path(paths):
            x = os.path.commonprefix(list(paths))
            while not x.endswith('/'):
                x = x[:-2]
            x
            return(x)


class Permission_mode():
    """
    Class to overload comparison operators to compare file permissions levels.

    'rw' > 'w' > 'r'
    """
    defined_modes = {'rw', 'w', 'r', 'ro'}

    def __init__(self, fs_str):

        self.mode = fs_str.mode if isinstance(
            fs_str,
            Permission_mode
        ) else 'ro' if fs_str=='r' else fs_str
        self.defined = self.mode in Permission_mode.defined_modes
        self._warn_if_undefined()

    def __repr__(self):
        return(self.mode)

    def __gt__(self, other):
        for permission in (self, other):
            if(permission._warn_if_undefined()):
                return(NotImplemented)

        if self.mode=='rw':
            if other.mode in {'w', 'ro'}:
                return(True)
        elif self.mode=='w' and other.mode=='ro':
            return(True)

        return(False)

    def __ge__(self, other):
        for permission in (self, other):
            if(permission._warn_if_undefined()):
                return(NotImplemented)

        if self.mode==other.mode or self>other:
            return(True)

        return(False)

    def __lt__(self, other):
        for permission in (self, other):
            if(permission._warn_if_undefined()):
                return(NotImplemented)

        if self.mode=='ro':
            if other.mode in {'w', 'rw'}:
                return(True)
        elif self.mode=='ro' and other.mode=='w':
            return(True)

        return(False)

    def __le__(self, other):
        for permission in (self, other):
            if(permission._warn_if_undefined()):
                return(NotImplemented)

        if self.mode==other.mode or self<other:
            return(True)

        return(False)

    def _warn_if_undefined(self):
        if not self.defined:
            warn(
                f'\'{self.mode}\' is not a fully-configured permission '
                f'level in {dist_name}. Configured permission levels are '
                f'''{", ".join([
                    f"'{mode}'" for mode in Permission_mode.defined_modes
                ])}''',
                UserWarning
            )
            return(True)
        return(False)