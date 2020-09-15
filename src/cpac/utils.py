import os
import yaml
import zlib
from base64 import b64encode, b64decode

from cpac import dist_name
from itertools import permutations
from warnings import warn
from unittest.mock import patch


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
        ) else 'ro' if fs_str == 'r' else fs_str
        self.defined = self.mode in Permission_mode.defined_modes
        self._warn_if_undefined()

    def __repr__(self):
        return(self.mode)

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
                    f"'{mode}'" for mode in Permission_mode.defined_modes
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


def render_crashfile(crash_path):
    """
    Parameter
    ---------
    crash_path: str

    Returns
    -------
    str, contents of pickle
    """


def traverse_deep(r, keys, setval=None):
    if setval is not None and "*" in keys:
        raise ValueError('"*" is not accepted when setting keys.')

    r0 = r

    slice_end = (None if setval is None else -1)
    for i, k in enumerate(keys[:slice_end]):
        if type(r) == dict:
            if k == '*':
                return {
                    kk: traverse_deep(r[kk], keys[i+1:])
                    for kk in r.keys()
                }

            if setval and k not in r:
                r[k] = {}
                return traverse_deep(r[k], keys[i+1:], setval)

            r = r[k]

        elif type(r) == list:
            if k == '*':
                return [
                    traverse_deep(rr, keys[i+1:])
                    for rr in r
                ]

            r = r[int(k)]

    if setval is not None:
        if type(r) == dict:
            r[keys[-1]] = setval
        elif type(r) == list:
            r[int(keys[-1])] = setval
        else:
            raise ValueError(f'Cannot set value for type "{type(r)}"')
        return r0

    return r


def parse_data_url(data_url):
    header, data = data_url.split(",", 1)
    media_type, *encoding = header[5:].lower().split(';')
    for enc in encoding:
        if enc == 'zlib':
            data = zlib.decompress(data)
        elif enc == 'base64':
            data = b64decode(data)
    return data, media_type


def generate_data_url(content, mime, compress=False):
    content = content.encode('utf-8')
    if compress:
        content = zlib.compress(content)
    return f"data:{mime};base64{';zlib' if compress else ''}," + b64encode(content).decode()


def yaml_parse(path_or_data_url):
    if path_or_data_url.lower().startswith('s3:'):
        raise ValueError('Cannot parse s3 URLs')

    if path_or_data_url.lower().startswith('data:'):
        data, _ = parse_data_url(path_or_data_url)
        config_data = yaml.safe_load(data)
        return config_data

    config_filename = os.path.realpath(path_or_data_url)
    if os.path.isdir(config_filename):
        raise ValueError('BIDS dataset')

    with open(config_filename, 'r') as f:
        config_data = yaml.safe_load(f)
        return config_data


def read_crash(crash_file):

    def accept_all(object, name, value):
        return value

    with patch('nipype.interfaces.base.traits_extension.File.validate', side_effect=accept_all):
        from nipype.utils.filemanip import loadcrash
        crash_data = loadcrash(crash_file)

        data = {
            "traceback": "".join(crash_data["traceback"])
        }
        if "node" in crash_data:
            node = crash_data["node"]
            data["node"] = {
                "name": str(node),
                "directory": node.output_dir(),
                "inputs": node.inputs.trait_get(),
            }
        return data