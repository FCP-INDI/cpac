import json
import asyncio
import tornado.httpclient as httpclient
from tornado.simple_httpclient import HTTPStreamClosedError
from tornado.websocket import websocket_connect


class Client:

    _http_client = None

    def __init__(self, server):
        self.server = f'{server[0]}:{server[1]}'

    async def __aenter__(self):
        self._http_client = httpclient.AsyncHTTPClient()
        while True:
            try:
                response = await self._http_client.fetch(f'http://{self.server}/')
            except (ConnectionError, HTTPStreamClosedError):
                await asyncio.sleep(1)
            except Exception as e:
                raise e
            else:
                self.info = json.loads(response.body)
                break

        return self

    def __await__(self):
        pass

    async def __aexit__(self, exc_type, exc, tb):
        self._http_client.close()
        self._http_client = None

    async def schedule(self, schedule):
        pass