import pytest

from adapter.main import app
from sanic.websocket import WebSocketProtocol

@pytest.yield_fixture
def app_srv():
    yield app

@pytest.fixture
def test_cli(loop, app_srv, test_client):
    return loop.run_until_complete(test_client(app_srv, protocol=WebSocketProtocol))