import os
import subprocess

def test_utils_help():
    o = subprocess.getoutput('cpac utils --help')

    assert "Docker" in o
    assert "COMMAND" in o

def test_utils_new_settings_template():
    import tempfile
    wd = tempfile.mkdtemp(prefix='cpac_pip_temp_')
    o = subprocess.getoutput(
        ' '.join([
            'cpac utils data_config new_settings_template',
            '--temp_dir',
            wd,
            '--working_dir',
            wd,
            '--output_dir',
            wd
        ])
    )

    template_path = os.path.join(wd, 'data_settings.yml')

    assert(os.path.exists(template_path))

    os.remove(template_path)
    os.rmdir(wd)
