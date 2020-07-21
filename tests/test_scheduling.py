import pytest
from cpac.api.scheduling import Scheduler
from cpac.api.schedules import Schedule, DataSettingsSchedule, DataConfigSchedule, ParticipantPipelineSchedule
from cpac.api.backends.base import Backend, BackendSchedule, RunStatus

from test_data.dummy import DummyBackend, DataSplitterSchedule


@pytest.mark.asyncio
async def test_scheduler():

    async with Scheduler(DummyBackend) as scheduler:

        schedule = scheduler.schedule(
            DataSplitterSchedule(
                data="My cRazY dATa"
            )
        )

        await scheduler

        sid = repr(schedule)
        statuses = await scheduler.statuses
        logs = await scheduler.logs

        assert len(statuses) == 4
        assert statuses[sid]['status'] == 'SUCCESS'
        assert 'parent' not in statuses[sid]
        assert len(statuses[sid]['children']) == 3

        assert schedule['text/pieces'] == ['My', 'cRazY', 'dATa']

        sid1, sid2, sid3 = statuses[sid]['children']
        assert statuses[sid1]['parent'] == sid
        assert statuses[sid2]['parent'] == sid
        assert statuses[sid3]['parent'] == sid
        assert statuses[sid1]['status'] == 'SUCCESS'
        assert statuses[sid2]['status'] == 'FAILED'
        assert statuses[sid3]['status'] == 'SUCCESS'


        assert len(logs) == 4
        assert 'parent' not in logs[sid]
        assert len(logs[sid]['children']) == 3
        assert 'length' in logs[sid]['logs'] and logs[sid]['logs']['length'] == 3

        sid1, sid2, sid3 = logs[sid]['children']
        assert logs[sid1]['parent'] == sid
        assert logs[sid2]['parent'] == sid
        assert logs[sid3]['parent'] == sid
        assert 'length' in logs[sid1]['logs'] and logs[sid1]['logs']['length'] == 2
        assert 'length' in logs[sid2]['logs'] and logs[sid2]['logs']['length'] == 5
        assert 'length' in logs[sid3]['logs'] and logs[sid3]['logs']['length'] == 4

        assert scheduler[sid1].schedule['text'] == 'MY'
        assert scheduler[sid2].schedule['text'] == 'CRAZY'
        assert scheduler[sid3].schedule['text'] == 'DATA'
