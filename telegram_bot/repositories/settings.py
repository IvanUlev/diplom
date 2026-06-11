from base import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.settings import Settings

class UsersRepository(BaseRepository[Settings]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Settings, session=session)
