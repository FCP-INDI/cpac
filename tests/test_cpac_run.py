import os
import subprocess
from utils import recursive_remove_dir

def test_utils_help():
    o = subprocess.getoutput('cpac run --help')

    assert "participant" in o

def test_utils_new_settings_template():
    import tempfile
    from datetime import date

    wd = tempfile.mkdtemp(prefix='cpac_pip_temp_')
    o = subprocess.getoutput(
        ' '.join([
            'cpac run s3://fcp-indi/data/Projects/ABIDE/RawDataBIDS/NYU',
            wd,
            'test_config --participant_ndx=2'
        ])
    )

    assert(
        any([date.today().isoformat() in fp for fp in os.listdir(wd)])
    )

    recursive_remove_dir(wd)
