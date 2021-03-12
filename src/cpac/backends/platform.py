import os
import pandas as pd
import pwd
import tempfile
import textwrap
import yaml

from collections import namedtuple
from contextlib import redirect_stderr
from io import StringIO
from tabulate import tabulate

from cpac.helpers import cpac_read_crash, get_extra_arg_value
from cpac.utils import Locals_to_bind, PermissionMode

Platform_Meta = namedtuple('Platform_Meta', 'name symbol')


class Backend(object):
    def __init__(self, **kwargs):
        # start with default pipline, but prefer pipeline config over preconfig
        # over default
        self.pipeline_config = '/cpac_resources/default_pipeline.yml'
        if 'extra_args' in kwargs and isinstance(kwargs['extra_args'], list):
            pipeline_config = get_extra_arg_value(
                kwargs['extra_args'], 'pipeline_file')
            if pipeline_config is not None:
                self.pipeline_config = yaml.safe_load(pipeline_config)
            else:
                pipeline_config = get_extra_arg_value(
                    kwargs['extra_args'], 'preconfig')
                if pipeline_config is not None:
                    self.pipeline_config = '/'.join([
                        '/code/CPAC/resources/configs',
                        f'pipeline_config_{pipeline_config}.yml'
                    ])

    def start(self, pipeline_config, subject_config):
        raise NotImplementedError()

    def read_crash(self, crashfile, flags=[], **kwargs):
        os.chmod(cpac_read_crash.__file__, 0o775)
        self._set_crashfile_binding(crashfile)
        if self.platform.name == 'Singularity':
            self._load_logging()
        stderr = StringIO()
        with redirect_stderr(stderr):
            del kwargs['command']
            crash_lines = list(self._read_crash(
                f'{cpac_read_crash.__file__} {crashfile}',
                **kwargs
            ))
            crash_message = ''.join([
                l.decode('utf-8') if isinstance(
                    l, bytes
                ) else l for l in (  # noqa: E741
                    [line[0] for line in crash_lines] if (
                        len(crash_lines) and isinstance(crash_lines[0], tuple)
                    ) else crash_lines
                )
            ])
            crash_message += stderr.getvalue()
            stderr.read()  # clear stderr
            print(crash_message.strip())
            if hasattr(self, 'container'):
                self.container.stop()

    def _bind_volume(self, local, remote, mode):
        local, remote = self._prep_binding(local, remote)
        b = {'bind': remote, 'mode': PermissionMode(mode)}
        if local in self.volumes:
            if remote in [binding['bind'] for binding in self.volumes[local]]:
                for i, binding in enumerate(self.volumes[local]):
                    self.volumes[local][i] = {
                        'bind': remote,
                        'mode': max([
                            self.volumes[local][i]['mode'], b['mode']
                        ])
                    }
            else:
                self.volumes[local].append(b)
        else:
            self.volumes[local] = [b]

    def _collect_config_binding(self, config, config_key):
        if isinstance(config, str):
            if os.path.exists(config):
                path = os.path.dirname(config)
                self._set_bindings({'custom_binding': [':'.join([path]*2)]})
                config = self.clarg(
                    clcommand='python -c "from CPAC.utils.configuration; '
                    'import Configuration; '
                    f'yaml.dump(Configuration({config}).dict())"'
                )
            config = yaml.safe_load(config)
        return config.get('pipeline_setup', {}).get(config_key, {}).get('path')

    def collect_config_bindings(self, config, **kwargs):
        kwargs['output_dir'] = kwargs.get(
            'output_dir',
            os.getcwd()
        )
        kwargs['working_dir'] = kwargs.get(
            'working_dir',
            os.getcwd()
        )

        config_bindings = {}
        cwd = os.getcwd()
        for c_b in {
            ('log_directory', 'log'),
            ('working_directory', 'working', 'working_dir'),
            ('crash_log_directory', 'log'),
            ('output_directory', 'outputs', 'output_dir')
        }:
            inner_binding = self._collect_config_binding(config, c_b[0])
            outer_binding = None
            if inner_binding is not None:
                if len(c_b) == 3:
                    if kwargs.get(c_b[2]) is not None:
                        outer_binding = kwargs[c_b[2]]
                    else:
                        kwargs[c_b[2]] = inner_binding
                try:
                    os.makedirs(inner_binding, exist_ok=True)
                except PermissionError:
                    outer_binding = os.path.join(kwargs.get(
                        'output_dir',
                        os.path.join(cwd, 'outputs')
                    ), c_b[1])
                if outer_binding is not None and inner_binding is not None:
                    config_bindings[outer_binding] = inner_binding
                elif outer_binding is not None:
                    config_bindings[outer_binding] = outer_binding
            else:
                path = os.path.join(cwd, c_b[1])
                config_bindings[path] = path
        kwargs['config_bindings'] = config_bindings
        return kwargs

    def _load_logging(self):
        t = pd.DataFrame([
            (i, j['bind'], j['mode']) for i in self.bindings['volumes'].keys(
            ) for j in self.bindings['volumes'][i]
        ])
        if not t.empty:
            t.columns = ['local', self.platform.name, 'mode']
            self._print_loading_with_symbol(
                " ".join([
                    self.image,
                    "with these directory bindings:"
                ])
            )
            print(textwrap.indent(
                tabulate(t.applymap(
                    lambda x: (
                        '\n'.join(textwrap.wrap(x, 42))
                    ) if isinstance(x, str) else x
                ), headers='keys', showindex=False),
                '  '
            ))
            print(
                f"Logging messages will refer to the {self.platform.name} "
                "paths.\n"
            )

    def _prep_binding(self, binding_path_local, binding_path_remote):
        binding_path_local = os.path.abspath(
            os.path.expanduser(binding_path_local)
        )
        os.makedirs(binding_path_local, exist_ok=True)
        return(
            os.path.realpath(binding_path_local),
            os.path.abspath(binding_path_remote)
        )

    def _print_loading_with_symbol(self, message, prefix='Loading'):
        if prefix is not None:
            print(prefix, end=' ')
        try:
            print(' '.join([self.platform.symbol, message]))
        except UnicodeEncodeError:
            print(message)

    def _set_bindings(self, **kwargs):
        tag = kwargs.get('tag', None)
        tag = tag if isinstance(tag, str) else None

        for kwarg in [
            *kwargs.get('extra_args', []), kwargs.get('crashfile', '')
        ]:
            if os.path.exists(kwarg):
                d = kwarg if os.path.isdir(kwarg) else os.path.dirname(kwarg)
                self._bind_volume(d, d, 'r')
        if 'data_config_file' in kwargs and isinstance(
            kwargs['data_config_file'], str
        ) and os.path.exists(kwargs['data_config_file']):
            dc_dir = os.path.dirname(kwargs['data_config_file'])
            self._bind_volume(dc_dir, dc_dir, 'r')
            locals_from_data_config = Locals_to_bind()
            locals_from_data_config.from_config_file(
                kwargs['data_config_file']
            )
            for local in locals_from_data_config.locals:
                self._bind_volume(local, local, 'r')
        self._bind_volume(kwargs['output_dir'], kwargs['output_dir'], 'rw')
        self._bind_volume(kwargs['working_dir'], kwargs['working_dir'], 'rw')
        if kwargs.get('custom_binding'):
            for d in kwargs['custom_binding']:
                self._bind_volume(*d.split(':'), 'rw')
        for d in ['bids_dir', 'output_dir']:
            if d in kwargs and isinstance(kwargs[d], str) and os.path.exists(
                kwargs[d]
            ):
                self._bind_volume(
                    kwargs[d],
                    kwargs[d],
                    'rw' if d == 'output_dir' else 'r'
                )
        if kwargs.get('config_bindings'):
            for binding in kwargs['config_bindings']:
                self._bind_volume(
                    binding,
                    kwargs['config_bindings'][binding],
                    'rw'
                )
        uid = os.getuid()
        self.bindings = {
            'gid': pwd.getpwuid(uid).pw_gid,
            'tag': tag,
            'uid': uid,
            'volumes': self.volumes
        }

    def _volumes_to_docker_mounts(self):
        return([
            '{}:{}:{}'.format(
                i,
                j['bind'],
                j['mode']
            ) for i in self.volumes.keys() for j in self.volumes[i]
        ])

    def _set_crashfile_binding(self, crashfile):
        for ckey in ["/wd/", "/crash/", "/log"]:
            if ckey in crashfile:
                self._bind_volume(crashfile.split(ckey)[0], '/outputs', 'rw')
        self._bind_volume(tempfile.TemporaryDirectory().name, '/out', 'rw')
        helper_dir = os.path.dirname(cpac_read_crash.__file__)
        self._bind_volume(helper_dir, helper_dir, 'ro')


class Result(object):
    mime = None

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __call__(self):
        yield self.value

    @property
    def description(self):
        return {
            'type': 'object'
        }


class FileResult(Result):

    def __init__(self, name, value, mime):
        self.name = name
        self.value = value
        self.mime = mime

    def __call__(self):
        with open(self.value, 'rb') as f:
            while True:
                piece = f.read(1024)
                if piece:
                    yield piece
                else:
                    return

    @property
    def description(self):
        return {
            'type': 'file',
            'mime': self.mime
        }
