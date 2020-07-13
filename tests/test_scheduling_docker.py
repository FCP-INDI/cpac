import os
import pytest
from cpac.api.scheduling import Scheduler
from cpac.api.schedules import Schedule, DataSettingsSchedule, DataConfigSchedule, ParticipantPipelineSchedule
from cpac.api.backends.docker import DockerBackend

from conftest import Constants
from test_data.dummy import DummyExecutor

try:
    from test_data.docker import build_image
except:
    pytest.skip("Skipping docker tests", allow_module_level=True)


@pytest.fixture(scope="module")
def docker_image():
    build_image(tag='docker-test')


def test_scheduler_docker(docker_image):
    scheduler = Scheduler(DockerBackend(tag='docker-test'), executor=DummyExecutor)

    schedule = scheduler.schedule(
        DataSettingsSchedule(
            data_settings=os.path.join(Constants.TESTS_DATA_PATH, 'data_settings_template.yml')
        )
    )

    assert len(schedule['data_config']) == 4
    assert all(s['site'] == 'NYU' for s in schedule['data_config'])
