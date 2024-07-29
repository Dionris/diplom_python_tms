import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode

import config
# from dotenv import find_dotenv, load_dotenv
#
# load_dotenv(find_dotenv())

# from middlewares.db import CounterMiddleWare

from middlewares.db import DataBaseSession
from database.engine import create_db, drop_db, session_maker

from handlers.user_private import user_private_router
from handlers.user_group import user_group_router
from handlers.admin_private import admin_router

from common.bot_cmds_list import private

from aiogram.client.default import DefaultBotProperties


# from aiogram.filters import CommandStart
# from aiogram.fsm.strategy import FSMStrategy
# from aiogram.types import BotCommandScopeAllPrivateChats

# ALLOWED_UPDATES = ['message, edited_message', 'callback_query']

# bot = Bot(token=os.getenv(TOKEN))  # можно и так спрятать токен
bot = Bot(token=config.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
bot.my_admins_list = []

# dp = Dispatcher(fsm_strategy=FSMStrategy.USER_IN_CHAT)
dp = Dispatcher()

#  срабатывает после фильтров
# admin_router.message.middleware(CounterMiddleWare())

#  срабатывает до фильтров
# admin_router.message.outer_middleware(CounterMiddleWare())

#  данный промежуточный слой срабатывает быстрее всех, он над всеми абдейтами
# dp.update.outer_middleware(CounterMiddleWare)

dp.include_router(user_private_router)
dp.include_router(user_group_router)
dp.include_router(admin_router)


async def on_startup(bot):
    run_param = False
    if run_param:
        await drop_db()

    await create_db()


async def on_shutdown(bot):
    print('бот лег')


async def main() -> None:
    # await create_db()
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot.delete_webhook(drop_pending_updates=True)  # сбрасывает старые обновления во время не работы
    # await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())  # Удалит кнопки
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    # await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)

    # это альтернатива ALLOWED_UPDATES
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

asyncio.run(main())
