from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.filters import ChatTypeFilter
from bot.keyboards import get_custom_callback_btns
import keyboards.btns as btns

from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.enums import ParseMode

from services.users.service import UsersService
from settings.logger import logger
from settings.telegram_routers import user_router
from bot.loader import bot
from texts import start_messages
import keyboards.btns as btns


user_router.message.filter(ChatTypeFilter(['private']))

@user_router.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext, session: AsyncSession) -> None:
    await state.set_state(None)
    user_service = UsersService(session)
    user = await user_service.check_user(message)

    await message.answer(
        text = start_messages.START_MESSAGE, 
        parse_mode=ParseMode.HTML,
        reply_markup=get_custom_callback_btns(
            btns=btns.START_BTNS,
            layout=btns.START_LAYOUT
            )
        )