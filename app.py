import os

from aiogram import Bot, Dispatcher, types
import asyncio

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.strategy import FSMStrategy
from aiogram.types import BotCommandScopeAllPrivateChats

import config
from config import TOKEN

# from dotenv import find_dotenv, load_dotenv
# load_dotenv(find_dotenv())

from handlers.user_private import user_private_router
from handlers.user_group import user_group_router
from handlers.admin_private import admin_router
from common.bot_cmds_list import private

ALLOWED_UPDATES = ['message, edited_message']

# bot = Bot(token=os.getenv(TOKEN))
bot = Bot(token=config.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
bot.my_admins_list = []

dp = Dispatcher(fsm_strategy=FSMStrategy.USER_IN_CHAT)

dp.include_router(user_private_router)
dp.include_router(user_group_router)
dp.include_router(admin_router)


async def main() -> None:
    await bot.delete_webhook(drop_pending_updates=True)  # сбрасывает старые обновления во время не работы
    # await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())  # Удалит кнопки
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)


asyncio.run(main())
