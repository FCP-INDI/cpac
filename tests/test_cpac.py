import pytest

from contextlib import redirect_stdout
from cpac.backends import Backends
from io import StringIO, TextIOWrapper, BytesIO


@pytest.mark.parametrize('platform', ['docker', 'singularity'])
def test_loading_message(platform):
    redirect_out = StringIO()
    with redirect_stdout(redirect_out):
        loaded = Backends(platform)
    with_symbol = ' '.join([
        'Loading',
        loaded.platform.symbol,
        loaded.platform.name
    ])
    assert with_symbol in redirect_out.getvalue()

    redirect_out = TextIOWrapper(
        BytesIO(), encoding='latin-1', errors='strict', write_through=True)
    with redirect_stdout(redirect_out):
        loaded = Backends(platform)
    without_symbol = ' '.join([
        'Loading',
        loaded.platform.name
    ])
    assert without_symbol in redirect_out.buffer.getvalue().decode()
