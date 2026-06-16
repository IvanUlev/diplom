from enums.enums import UserRole
from repositories.users import UsersRepository
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.users import Users
from aiogram import types

class UsersService:
    """Сервис для работы с пользователями"""
    def __init__(self, session: AsyncSession):
        self.repo = UsersRepository(session)

    async def check_user(self, message: types.Message) -> Users:
        """
        Проверка существования пользователя по Telegram ID
        Если не существует, то создает нового
        Возвращает пользователя
        """
        user = await self.repo.get_by_telegram_id(message.from_user.id)

        if not user:
            user = await self.repo.add(Users(
                telegram_id=message.from_user.id,
                username=message.from_user.username or "Unknown",
                name=message.from_user.full_name,
                role=UserRole.USER.value
            ))
        
        return user
    
    async def is_admin(self, message: types.Message) -> bool:
        """Проверка, является ли пользователь админом"""
        user = await self.check_user(message)
        return user.role == UserRole.ADMIN.value
    


