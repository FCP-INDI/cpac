import pytest
import sys

from cpac.backends import Backends


@pytest.mark.parametrize('platform', ['docker', 'singularity'])
def test_loading_message(capsys, platform):
    loaded = Backends(platform)
    captured = capsys.readouterr()
    assert captured.out.split('\n')[0].strip() == ' '.join([
        'Loading',
        loaded.platform.symbol,
        loaded.platform.name
    ])
    sys.stdout.reconfigure(encoding='latin-1')
    loaded = Backends(platform)
    captured = capsys.readouterr()
    assert captured.out.split('\n')[0].strip() == ' '.join([
        'Loading',
        loaded.platform.name
    ])
