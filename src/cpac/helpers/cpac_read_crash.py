#!/usr/bin/env python

import os
import re

from nipype import __version__ as nipype_version
from nipype.utils.filemanip import loadcrash
from traits.trait_errors import TraitError
from sys import argv

path_regex = re.compile(
    "(?<=((a value of ')|( the path  '))).*(?=((' <class)|(' does)))"
)


def read_crash(path, touch_dir=None):
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
    print(f'Nipype version {nipype_version}')
    read_crash(argv[1])
