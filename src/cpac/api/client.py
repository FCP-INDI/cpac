import json
import asyncio
import logging
import tornado.httpclient as httpclient
from tornado.simple_httpclient import HTTPStreamClosedError, HTTPTimeoutError
from tornado.websocket import websocket_connect

from .schedules import (DataConfigSchedule, DataSettingsSchedule,
                         ParticipantPipelineSchedule, Schedule)

logger = logging.getLogger(__name__)

class Client:

    _http_client = None

    def __init__(self, server):
        self.server = f'{server[0]}:{server[1]}'

    async def __aenter__(self):
        self._http_client = httpclient.AsyncHTTPClient()
        while True:
            try:
                response = await self._http_client.fetch(f'http://{self.server}/')
            except (ConnectionError, HTTPStreamClosedError, HTTPTimeoutError):
                await asyncio.sleep(1)
            except Exception as e:
                raise e
            else:
                self.info = json.loads(response.body)
                logger.info(f'[Client] Info {self.info}')
                break

        return self

    def __await__(self):
        pass

    async def __aexit__(self, exc_type, exc, tb):
        self._http_client.close()
        self._http_client = None

    async def schedule(self, schedule):
        if not isinstance(schedule, (DataConfigSchedule, DataSettingsSchedule)):
            raise ValueError("Must be DataSettingsSchedule or DataConfigSchedule schedule")

        try:
            schedule_type = None
            if isinstance(schedule, DataSettingsSchedule):
                schedule_type =  "data_settings"
            elif isinstance(schedule, DataConfigSchedule):
                schedule_type =  "pipeline"

            response = await self._http_client.fetch(
                f'http://{self.server}/schedule',
                method='POST',
                body=json.dumps({
                    "type": schedule_type,
                    **schedule.__json__(),
                })
            ) 
        except Exception as e:
            raise e
        else:
            data = json.loads(response.body)['schedule']
            logger.info(f'[Client] Scheduled {data}')
            return data

    async def listen(self, schedule, children=True):

        from .backends.base import BackendSchedule
        event_types = {
            'Spawn': Schedule.Spawn,
            'Start': Schedule.Start,
            'End': Schedule.End,
            'Log': BackendSchedule.Log,
            'Status': BackendSchedule.Status,
        }

        uri = f'ws://{self.server}/schedule/connect'
        logger.info(f'[Client] Listen {uri}')

        ws = await websocket_connect(uri)

        msg = await ws.read_message()
        if msg is None:
            return

        logger.info(f'[Client] WS Info {msg}')

        schedules_alive = set([schedule])

        await ws.write_message(json.dumps({
            'type': 'watch',
            'schedule': schedule,
            'watchers': ['Spawn', 'Start', 'End', 'Log', 'Status'],
            'children': True,
        }))

        while len(schedules_alive) > 0:
            msg = await ws.read_message()
            if msg is None:
                break
            msg = json.loads(msg)
            if msg['type'] != 'watch':
                continue
                
            data = msg['data']
            message_type = data['type']
            message = data['message']
        
            if message_type == 'Spawn':
                schedules_alive |= set([message['child']])
            if message_type == 'End':
                schedules_alive ^= set([message['schedule']])

            yield event_types[data['type']](**message)

        ws.close()