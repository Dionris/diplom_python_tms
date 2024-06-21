from aiogram import Bot, Dispatcher, types
import asyncio
from aiogram.filters import CommandStart
from data.config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_cmd(message: types.Message) -> None:
    await message.answer('Это была команда старт')


@dp.message()
async def echo(message: types.Message):
    await message.answer(message.text)  # просто ответит
    await message.reply(message.text)  # упомянет автора


async def main() -> None:
    await bot.delete_webhook(drop_pending_updates=True)  # сбрасывает старые обновления во время не работы
    await dp.start_polling(bot)


asyncio.run(main())
