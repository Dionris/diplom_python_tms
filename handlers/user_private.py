from aiogram import types, Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, or_f
from aiogram.utils.formatting import as_list, as_marked_section, Bold

from filters.chat_types import ChatTypesFilter

from kbds import reply

user_private_router = Router()
user_private_router.message.filter(ChatTypesFilter(['private']))


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message) -> None:
    await message.answer('Привет я виртуальный помощник',
                         reply_markup=reply.stat_kb3.as_markup(
                             resize_keyboard=True,
                             input_field_placeholder="что вас интересует?"))


# убрал для работы фильира запрещенных слов
# @user_private_router.message((F.text.lower().contains('вариант')) | (F.text.lower() == 'вариант'))  # | или
# @user_private_router.message(F.text, F.text.lower().contains('вариант'))  # 2 проверки
# @user_private_router.message(~(F.text.lower().contains('вариант')))  # реверсирует вырожение
# @user_private_router.message(F.text.lower().contains('вариант'))  # в контесте
# @user_private_router.message(F.text.lower() == 'вариант')
# @user_private_router.message(Command('menu'))


@user_private_router.message(or_f(Command('menu'), (F.text.lower() == "меню")))
async def menu_cmd(message: types.Message):
    await message.answer("Вот меню:", reply_markup=reply.del_kb)


@user_private_router.message(F.text.lower() == "о магазине")
@user_private_router.message(Command('about'))
async def about_cmd(message: types.Message):
    await message.answer("О нас:")


@user_private_router.message(F.text.lower() == "варианты оплаты")
@user_private_router.message(Command('payment'))
async def payment_cmd(message: types.Message):

    text = as_marked_section(
        Bold("Варианты оплаты:"),
        "Картой в боте",
        "При получении карта/кеш",
        "В заведении",
        marker='✅ '
    )
    await message.answer(text.as_html())


@user_private_router.message(
    (F.text.lower().constains("доставк")) | (F.text.lower() == "варианты доставки")
)
@user_private_router.message(Command('shipping'))
async def shipping_cmd(message: types.Message):
    # await message.answer("<b>Варианты доставки:</b>", parse_mode=ParseMode.HTML)  # не красиво

    #  ниже как можно сделать красивее, плюс еще нужно будет в app.py к токену добавить parse_mode
    text = as_list(
        as_marked_section(
            Bold('Варианты доставки/заказа:'),
            'Курьер',
            'Самовывоз (сейчас прибегу заберу)',
            'Покушаю у вас (сейчас прибегу)',
            marker='✅ '
        ),
        as_marked_section(
            Bold('Нельзя:'),
            'голуби',
            'Почта',
            marker='❌ '
        ),
        sep='\n\n--------------------\n\n'
    )

    await message.answer(text.as_html())


# @user_private_router.message()
# async def echo(message: types.Message):
#     await message.answer(message.text)  # просто ответит
#     await message.reply(messag e.text)  # упомянет автора


@user_private_router.message(F.contact)
async def get_contact(message: types.Message):
    await message.answer(f'номер получен')
    await message.answer(str(message.contact))


@user_private_router.message(F.location)
async def get_location(message: types.Message):
    await message.answer(f'локация получена')
    await message.answer(str(message.location))
