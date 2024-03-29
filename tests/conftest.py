import pytest
from aiopg.sa import create_engine

from config import get_config
from dl.repository import Repository


class DatabaseConfig:
    def __init__(self, dsn):
        self.dsn = dsn
        self.timeout = 10


@pytest.fixture(scope='session')
def db_config():
    return get_config().db


@pytest.fixture
async def repository(loop, db_config) -> Repository:
    return await Repository(db_config).__aenter__()


async def fill_db(connection):

    await connection.execute(
        '''INSERT INTO location (id, latitude, longitude) 
        VALUES (1, '123.23123', '87.323'), (2, '163.543', '13.3675')'''
    )

    await connection.execute(
        '''INSERT INTO "user" 
        (id, full_name, password_hash, is_admin, location_id) 
        VALUES (1, 'Caroline Pospelova', 'password', False,  1), 
        (2, 'Nik Pospelov', 'password2', False, 2)
        '''
    )


async def clean_db(connection):
    await connection.execute('''DELETE FROM "user"''')
    await connection.execute('''DELETE FROM location''')


@pytest.fixture
async def test_db(db_config):
    engine = await create_engine(db_config.dsn)
    async with engine.acquire() as connection:
        await fill_db(connection)
        yield
        await clean_db(connection)

