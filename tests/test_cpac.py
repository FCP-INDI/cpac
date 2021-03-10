from contextlib import redirect_stdout
from io import StringIO, TextIOWrapper, BytesIO

from cpac.backends import Backends


def test_loading_message(platform, tag):
    redirect_out = StringIO()
    with redirect_stdout(redirect_out):
        loaded = Backends(platform, tag=tag)
    with_symbol = ' '.join([
        'Loading',
        loaded.platform.symbol,
        loaded.platform.name
    ])
    assert with_symbol in redirect_out.getvalue()

    redirect_out = TextIOWrapper(
        BytesIO(), encoding='latin-1', errors='strict', write_through=True)
    with redirect_stdout(redirect_out):
        loaded = Backends(platform, tag=tag)
    without_symbol = ' '.join([
        'Loading',
        loaded.platform.name
    ])
    assert without_symbol in redirect_out.buffer.getvalue().decode()
