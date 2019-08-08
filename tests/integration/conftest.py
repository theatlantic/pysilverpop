import pytest

from silverpop import api
from tests import mock_env  # TODO: mock_env


@pytest.fixture
def silverpop_client_fixture():
    return api.Silverpop(**mock_env.SILVERPOP['KEYS'])
