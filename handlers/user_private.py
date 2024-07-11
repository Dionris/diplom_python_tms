from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command

from filters.chat_types import ChatTypesFilter

user_private_router = Router()
user_private_router.message.filter(ChatTypesFilter(['private']))



@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message) -> None:
    await message.answer('Приает я виртуальный помощник')


# убрал для работы фильира запрещенных слов
# @user_private_router.message((F.text.lower().contains('вариант')) | (F.text.lower() == 'вариант'))  # | или
# @user_private_router.message(F.text, F.text.lower().contains('вариант'))  # 2 проверки
# @user_private_router.message(~(F.text.lower().contains('вариант')))  # реверсирует вырожение
# @user_private_router.message(F.text.lower().contains('вариант'))  # в контесте
# @user_private_router.message(F.text.lower() == 'вариант')
# @user_private_router.message(Command('menu'))
# async def menu_cmd(message: types.Message):
#     await message.answer("Вот меню:")


@user_private_router.message(Command('about'))
async def about_cmd(message: types.Message):
    await message.answer("О нас:")


@user_private_router.message(Command('payment'))
async def payment_cmd(message: types.Message):
    await message.answer("Варианты оплаты:")


@user_private_router.message(Command('shipping'))
async def shipping_cmd(message: types.Message):
    await message.answer("Варианты доставки:")

# @user_private_router.message()
# async def echo(message: types.Message):
#     await message.answer(message.text)  # просто ответит
#     await message.reply(messag e.text)  # упомянет автора
