#!/usr/bin/env python
'''cpac_read_crash.py

`cpac_read_crash` is intended to be run inside a C-PAC container.
The current run environment does not include the package `nipype`.
'''

import os
import re

from sys import argv

path_regex = re.compile(
    "(?<=((a value of ')|( the path  '))).*(?=((' <class)|(' does)))"
)


class NoNipype(ModuleNotFoundError):
    def __init__(self, msg=None, *args, **kwargs):
        no_nipype_message = __doc__.lstrip('cpac_read_crash.py').lstrip()
        self.msg = '\n'.join([
            msg, no_nipype_message
        ]) if msg is not None else no_nipype_message
        self.args = (self.msg,)


def read_crash(path, touch_dir=None):
    try:
        from nipype.utils.filemanip import loadcrash
        from traits.trait_errors import TraitError
    except ModuleNotFoundError:
        raise NoNipype from None

    try:
        crash_report = '\n'.join(loadcrash(path).get('traceback', []))
        print(crash_report)
    except TraitError as e:
        touched_dir = _touch_trait_error_path(e.args[0])
        if (touch_dir and touched_dir != touch_dir) or (not touch_dir):
            # Disallow repeated attempts to touch the same file
            read_crash(path, touched_dir)


def _touch_trait_error_path(crash_message):
    print(crash_message)
    match = path_regex.search(crash_message)
    if match:
        print(f'\nTouching "{match[0]}" …\n')
        os.makedirs(os.path.dirname(match[0]), exist_ok=True)
        with open(match[0], 'w') as fp:
            fp.write('')
        return(match)


if __name__ == '__main__':
    try:
        from nipype import __version__ as nipype_version
    except ModuleNotFoundError:
        raise NoNipype from None
    print(f'Nipype version {nipype_version}')
    read_crash(argv[1])
