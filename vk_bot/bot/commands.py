from aiogram import types, Bot


BOT_COMMANDS = [
    types.BotCommand(command="start", description="Начало работы с ботом"),
]

async def setup_bot_commands(bot: Bot) -> None:
    """Устанавливает команды бота"""
    await bot.set_my_commands(
        BOT_COMMANDS, 
        scope=types.BotCommandScopeAllPrivateChats()
    )