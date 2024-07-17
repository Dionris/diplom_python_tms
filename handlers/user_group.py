from string import punctuation

from aiogram import types, Router, F, Bot
from aiogram.filters import Command

from filters.chat_types import ChatTypesFilter
from common.restricted_words import restricted_words

user_group_router = Router()
user_group_router.message.filter(ChatTypesFilter(['group', 'supergroup']))
user_group_router.edited_message.filter(ChatTypesFilter(['group', 'supergroup']))


@user_group_router.message(Command('admin'))
async def get_admins(message: types.Message, bot: Bot):
    chat_id = message.chat.id
    admins_list = await bot.get_chat_administrators(chat_id)
    #  просмотреть все данные и свойства полученных объектов
    # print(admin_list)
    #  Код ниже это генератор списка, как и этот  x = [i for i in range(10)]
    admins_list = [
        member.user.id
        for member in admins_list
        if member.status == 'creator' or member.status == 'administrator'
    ]
    bot.my_admins_list = admins_list
    if message.from_user.id in admins_list:
        await message.delete()
    # print(admins_list)


def clean_text(text: str):
    return text.translate(str.maketrans('', '', punctuation))


#  Фильтр например - х!ом"як


@user_group_router.edited_message()
@user_group_router.message()
async def cleanner(message: types.Message):
    if restricted_words.intersection(clean_text(message.text.lower()).split()):
        await message.answer(
            f"{message.from_user.first_name}, соблюдайте порядок в чате!"
        )
        await message.delete()
        # await message.chat.ban(message.from_user.id)  #  ban user
