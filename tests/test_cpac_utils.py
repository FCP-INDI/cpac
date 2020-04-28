import os
from contextlib import redirect_stdout
from cpac.__main__ import main
from io import StringIO
from utils import recursive_remove_dir

def test_utils_help():
    f = StringIO()
    with redirect_stdout(f):
        main('cpac utils --help'.split(' '))
    o = f.getvalue()

    assert "Docker" in o
    assert "COMMAND" in o

def test_utils_new_settings_template():
    import tempfile
    wd = tempfile.mkdtemp(prefix='cpac_pip_temp_')
    f = StringIO()
    with redirect_stdout(f):
        main((
            f'cpac --working_dir {wd} --temp_dir {wd} --output_dir {wd} '
            f'utils data_config new_settings_template'
        ).split(' '))

    o = f.getvalue()

    template_path = os.path.join(wd, 'data_settings.yml')

    assert(os.path.exists(template_path))

    recursive_remove_dir(wd)
