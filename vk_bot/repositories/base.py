from typing import TypeVar, Generic, Optional, Union
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations."""

    def __init__(self, model: type[ModelType], session: AsyncSession):
        self._model = model
        self._session = session

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        query = select(self._model).where(self._model.id == id)
        result = await self._session.execute(query)
        return result.scalar()

    async def get_all(self) -> list[ModelType]:
        query = select(self._model)
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def add(self, obj: ModelType) -> ModelType:
        self._session.add(obj)
        await self._session.commit()
        await self._session.refresh(obj)
        return obj
    
    async def update(
        self,
        id: int,
        data: Union[ModelType, dict],
        allow_none: bool = False,
    ) -> ModelType:
        """
        Update entity by id.
        
        Args:
            id: Entity ID
            data: ORM object or dict with fields to update
            allow_none: If True, None values will be set. If False, None values are skipped.
        """
        obj = await self.get_by_id(id)

        if not obj:
            raise ValueError(f"{self._model.__name__} with id {id} not found.")

        update_data = self._extract_update_data(data, allow_none)

        for key, value in update_data.items():
            if hasattr(obj, key) and key != "id":
                setattr(obj, key, value)

        await self._session.commit()
        await self._session.refresh(obj)
        return obj
    
    def _extract_update_data(
        self,
        data: Union[ModelType, dict],
        allow_none: bool,
    ) -> dict:
        """Extract update data from ORM object or dict."""
        if isinstance(data, dict):
            if allow_none:
                return data
            return {k: v for k, v in data.items() if v is not None}

        return {
            key: value
            for key, value in data.__dict__.items()
            if not key.startswith("_") and (allow_none or value is not None)
        }

    async def delete(self, id: int) -> ModelType:
        obj = await self.get_by_id(id)

        if not obj:
            raise ValueError(f"{self._model.__name__} with id {id} not found.")

        await self._session.delete(obj)
        await self._session.commit()

        return obj
