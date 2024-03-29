from aiopg.sa import create_engine
from aiopg.sa.result import RowProxy
from sqlalchemy import select, join
from sqlalchemy.sql import Selectable
from typing import Any, List, Dict, Type

from config import DatabaseConfig
from dl.models.base_model import BaseModel
from dl.models.location import LocationModel
from dl.models.user import UserModel


class Repository:
    __slots__ = ('_dsn', '_engine', 'timeout')

    def __init__(self, config: DatabaseConfig) -> None:
        self._dsn = config.dsn
        self.timeout = config.timeout

    async def __aenter__(self) -> 'Repository':
        self._engine = await create_engine(self._dsn, timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self._engine.close()
        await self._engine.wait_closed()

    async def _execute(self, query: Selectable) -> Any:
        async with self._engine.acquire() as connection:
            return await connection.execute(query)

    async def _fetchall(self, query: Selectable) -> List[RowProxy]:
        async with self._engine.acquire() as connection:
            cursor = await connection.execute(query)
            resp: List[RowProxy] = await cursor.fetchall()
            return resp

    async def _first(self, query: Selectable) -> RowProxy:
        async with self._engine.acquire() as connection:
            cursor = await connection.execute(query)
            resp: RowProxy = await cursor.first()
            return resp

    async def _scalar(self, query: Selectable) -> Any:
        async with self._engine.acquire() as connection:
            return await connection.scalar(query)

    async def insert_row_to_model(
        self, model: Type[BaseModel], **kwargs: Dict[str, Any]
    ) -> int:
        await model.check_types(data=kwargs)
        return await self._scalar(
            model.__table__
            .insert()
            .values(**kwargs)
            .returning(model.id)
        )

    async def select_from_model_by_ids(
        self, model: Type[BaseModel], ids: List[int]
    ) -> List[RowProxy]:
        return await self._fetchall(
            select(model).where(model.id.in_(ids))
        )

    async def select_user_full_info_by_id(self, id: int) -> RowProxy:
        return await self._first(
            select(
                UserModel.id, UserModel.full_name,
                LocationModel.longitude, LocationModel.latitude
            )
            .select_from(join(UserModel, LocationModel))
            .where(UserModel.id == id)
        )

    async def select_user_login_data(self, full_name: str) -> RowProxy:
        return await self._first(
            select(UserModel.id, UserModel.password_hash)
            .where(UserModel.full_name == full_name).apply_labels()
        )

    async def delete_row_to_model_by_id(
        self, model: Type[BaseModel], id: int
    ) -> None:
        return await self._execute(
            model.__table__.delete().where(model.id == id)
        )
