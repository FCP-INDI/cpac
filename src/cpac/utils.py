import sys

PY3 = sys.version_info[0] == 3

if PY3:
    string_types = str,
else:
    string_types = basestring,


_bytes = bytes
if PY3:
    bytes = lambda data: _bytes(data, 'utf8')
else:
    bytes = lambda data: _bytes(data, 'utf8')


try:
    from urllib.parse import urlparse, urlencode
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
except ImportError:
    from urlparse import urlparse
    from urllib import urlencode
    from urllib2 import urlopen, Request, HTTPError