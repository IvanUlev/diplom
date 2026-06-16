from repositories.base import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.users import Users
from sqlalchemy import select

class UsersRepository(BaseRepository[Users]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Users, session=session)

    async def get_by_telegram_id(self, telegram_id: int) -> Users:
        query = select(Users).where(Users.telegram_id == telegram_id)
        result = await self._session.execute(query)
        return result.scalar()
    