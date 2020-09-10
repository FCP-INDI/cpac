import json
import asyncio
import logging
import tornado.httpclient as httpclient
from tornado.simple_httpclient import HTTPStreamClosedError, HTTPTimeoutError
from tornado.websocket import websocket_connect

from .schedules import (DataConfigSchedule, DataSettingsSchedule,
                         ParticipantPipelineSchedule, Schedule,
                         schedules)

logger = logging.getLogger(__name__)

class Client:

    _http_client = None
    _schedule_mapping = {}

    def __init__(self, server):
        self.server = f'{server[0]}:{server[1]}'

    async def __aenter__(self):
        self._http_client = httpclient.AsyncHTTPClient(force_instance=True)
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
        try:
            if isinstance(schedule, DataSettingsSchedule):
                schedule_type =  "data_settings"
            elif isinstance(schedule, DataConfigSchedule):
                schedule_type =  "pipeline"
            elif isinstance(schedule, ParticipantPipelineSchedule):
                schedule_type =  "participant"

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
            self.map(schedule, data)
            logger.info(f'[Client] Scheduled {data}')
            return data

    async def result(self, schedule, mapped=True):
        try:
            if mapped:
                schedule = self[schedule]

            response = await self._http_client.fetch(
                f'http://{self.server}/schedule/{schedule}/result',
                method='GET'
            )
        except Exception as e:
            raise e
        else:
            if response.code == 425:
                return None

            data = json.loads(response.body)
            return data['result']

    async def metadata(self, schedule, mapped=True):
        try:
            if mapped:
                schedule = self[schedule]

            response = await self._http_client.fetch(
                f'http://{self.server}/schedule/{schedule}/metadata',
                method='GET'
            )
        except Exception as e:
            raise e
        else:
            data = json.loads(response.body)
            metadata = data['metadata']
            logger.info(f'[Client] Metadata {metadata}')
            return metadata

    def __getitem__(self, key):
        if isinstance(key, Schedule):
            key = repr(key)

        if key not in self._schedule_mapping:
            raise ValueError(f'Schedule {key} does not exist. Actual keys: {list(self._schedule_mapping)}')

        return self._schedule_mapping[key]

    def map(self, schedule, remote_schedule):
        if isinstance(schedule, Schedule):
            schedule = repr(schedule)
        self._schedule_mapping[schedule] = remote_schedule

    async def listen(self, schedule, children=True, mapped=True):
        if mapped:
            schedule = self[schedule]

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
                logger.info(f'[Client] Spawn received for {message["child"]}, alive: {list(schedules_alive)}')

            if message_type == 'End':
                schedules_alive ^= set([message['schedule']])
                logger.info(f'[Client] End received for {message["schedule"]}, alive: {list(schedules_alive)}')

            logger.info(f'[Client] Message {msg}')

            message['schedule'] = await (ScheduleProxy(message['schedule'])(self))
            if message_type == 'Spawn':
                message['child'] = await (ScheduleProxy(message['child'])(self))

            yield event_types[message_type](**message)

        logger.info(f'[Client] Finished listening for {schedule}')
        ws.close()


class ScheduleProxy:

    _types = {
        schedule.__name__: schedule
        for schedule in schedules
    }

    def __init__(self, schedule):
        self._schedule = schedule

    async def __call__(self, client):
        meta = await client.metadata(self._schedule, mapped=False)
        inst = self._types[meta['type']](**meta['parameters'])
        client.map(inst, meta['id'])
        return inst