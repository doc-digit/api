import pytest
import gino
import sqlalchemy


from sanic.websocket import WebSocketProtocol
from api.main import app
from api.database import db


DB_HOST = 'localhost'
DB_PORT = '5432'
DB_USER = 'docdigit'
DB_PASSWORD = '12345'
DB_DATABASE = 'docdigit'
PG_URL = 'postgresql://{}:{}@{}:{}/{}'.format(DB_USER,DB_PASSWORD,DB_HOST,DB_PORT,DB_DATABASE)

@pytest.yield_fixture
def app_srv():
    yield app

@pytest.fixture
def test_cli(loop, app_srv, test_client):
    return loop.run_until_complete(test_client(app_srv, protocol=WebSocketProtocol))

@pytest.fixture(scope='module')
def db_engine():
    rv = sqlalchemy.create_engine(PG_URL)

    db.create_all(rv)
    yield rv
    db.drop_all(rv)
    rv.dispose()

@pytest.fixture
async def engine(db_engine):
    async with db.with_bind(PG_URL) as e:
        yield e
