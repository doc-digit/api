import pytest

from api.main import app

from starlette.testclient import TestClient


@pytest.fixture
def client():
    yield TestClient(app)
