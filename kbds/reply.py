from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, KeyboardButtonPollType
from aiogram.utils.keyboard import ReplyKeyboardBuilder


# stat_kb = ReplyKeyboardMarkup(
#     keyboard=[
#         [
#             KeyboardButton(text="Меню"),
#             KeyboardButton(text="О магазине"),
#         ],
#         [
#             KeyboardButton(text="Варианты доставки"),
#             KeyboardButton(text="Варианты оплаты"),
#         ]
#     ],
#     resize_keyboard=True,
#     input_field_placeholder="что вас интересует?"
# )
#
# del_kb = ReplyKeyboardRemove()
#
#
# stat_kb2 = ReplyKeyboardBuilder()
# stat_kb2.add(
#     KeyboardButton(text="Меню"),
#     KeyboardButton(text="О магазине"),
#     KeyboardButton(text="Варианты доставки"),
#     KeyboardButton(text="Варианты оплаты"),
# )
# stat_kb2.adjust(2, 2)
#
#
# stat_kb3 = ReplyKeyboardBuilder()
# stat_kb3.attach(stat_kb2)
# # stat_kb3.add(KeyboardButton(text="Оставить отзыв"),)
# # stat_kb3.adjust(2, 2)
# # или можно так написать
# stat_kb3.row(KeyboardButton(text="Оставить отзыв"),)
#
#
# test_kb = ReplyKeyboardMarkup(
#     keyboard=[
#         [
#             KeyboardButton(text="Создать опрос", request_poll=KeyboardButtonPollType()),
#         ],
#         [
#             KeyboardButton(text="Отправить номер ☎️", request_contact=True),
#             KeyboardButton(text="Отправить локацию 🗺", request_contact=True),
#         ],
#     ],
#     resize_keyboard=True,
# )

def get_keyboard(
        *btns: str,
        placeholder: str = None,
        request_contact: int = None,
        requrst_location: int = None,
        sizes: tuple[int] = (2,),

):
    '''
    Parameters request_contrct and requrst_location must be as ingexes of btns args for buttons you need:
    Exemple:
    get_keyboards(
        'меню:',
        'О магазине',
        'Варианты оплаты',
        'Варианты доставки',
        'Отправить номер телефона',
        placeholder='Что вас интересует?',
        request_contact=4,
        sizes=(2, 2, 1)
        )
    '''
    keyboard = ReplyKeyboardBuilder()

    for index, text in enumerate(btns, start=0):

        if request_contact and request_contact == index:
            keyboard.add(KeyboardButton(text=text, request_contact=True))

        elif requrst_location and requrst_location == index:
            keyboard.add(KeyboardButton(text=text, request_location=True))

        else:
            keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True, input_field_placeholder=placeholder
    )
