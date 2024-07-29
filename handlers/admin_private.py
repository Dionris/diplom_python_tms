from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from sqlalchemy.ext.asyncio import AsyncSession

# from database.models import Product
from database.orm_query import (
    orm_add_product,
    orm_get_product,
    orm_get_products,
    orm_delete_product,
    orm_update_product
)

from filters.chat_types import ChatTypesFilter, IsAdmin

from kbds.inline import get_callback_btns
from kbds.reply import get_keyboard

admin_router = Router()
admin_router.message.filter(ChatTypesFilter(['private']), IsAdmin())

ADMIN_KB = get_keyboard(
    'Добавить товар',
    'Асортимент',
    # 'Изменить товар',
    # 'Удалить товар',
    # 'Я так, просто посмотреть зашел',
    placeholder='Выберите действие',
    # sizes=(2, 1, 1),
    sizes=(2,),
)


class AddProduct(StatesGroup):
    # шаги состояния
    name = State()
    description = State()
    price = State()
    image = State()

    product_for_change = None

    texts = {
        'AddProduct:name': 'Введите название заново:',
        'AddProduct:description': 'Введите описание заново:',
        'AddProduct:price': 'Введите стоимость заново:',
        'AddProduct:image': 'Этот стейт последний))',
    }


@admin_router.message(Command('admin'))
async def add_product(message: types.Message):
    await message.answer('Что хотите сделать?', reply_markup=ADMIN_KB)


@admin_router.message(F.text == 'Асортимент')
async def starting_at_product(message: types.Message, session: AsyncSession):
    for product in await orm_get_products(session):
        await message.answer_photo(
            product.image,
            caption=f"<strong>{product.name}\
                   </strong>\n{product.description}\nСтоимость: {round(product.price, 2)}",
            reply_markup=get_callback_btns(btns={
                'Удалить': f'delete_{product.id}',
                'Изменить': f'change_{product.id}',

            })
        )
    await message.answer('Ок, вот список товаров ⬆️')


@admin_router.callback_query(F.data.startswith('delete_'))
async def delete_product_callback(callback: types.CallbackQuery, session: AsyncSession):
    product_id = callback.data.split("_")[-1]
    await orm_delete_product(session, int(product_id))

    await callback.answer("Товар удален")
    await callback.message.answer("Товар удален!")


# @admin_router.message(F.text == 'Я так, просто посмотреть зашел')
# async def starting_at_product(message: types.Message):
#     await message.answer('Ок, вот список товаров ⬆️')
#
#
# @admin_router.message(F.text == 'Изменить товар')
# async def change_product(message: types.Message):
#     await message.answer('Ок, вот список товаров ⬆️')


# @admin_router.message(F.text == 'Удалить товар')
# async def delete_product(message: types.Message):
#     # async def delete_product(message: types.Message, counter):  #  для теста
#     #     print(counter)
#     await message.answer('Выберите товар(ы) для удаления ⬆️')


#  Код ниже для машины состояний (FSM)


@admin_router.callback_query(StateFilter(None), F.data.startswith('change_'))
async def change_product_callback(
        callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    product_id = callback.data.split("_")[-1]

    product_for_change = await orm_get_product(session, int(product_id))

    AddProduct.product_for_change = product_for_change

    await callback.answer()
    await callback.message.answer(
        "Введите название товара", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddProduct.name)


#  Становимся в состояние ожидания ввода name
@admin_router.message(StateFilter(None), F.text == 'Добавить товар')
async def add_product(message: types.Message, state: FSMContext):
    await message.answer(
        'Введите название товара', reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddProduct.name)


#  Хендлер отмены и сброса состояния должен быть всегда именно здесь
#  после того как встали в состояние номер 1 (злементарная очередность фильтров)
@admin_router.message(StateFilter('*'), Command('отмена'))
@admin_router.message(StateFilter('*'), F.text.casefold() == 'отмена')
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    if AddProduct.product_for_change:
        AddProduct.product_for_change =None

    await state.clear()
    await message.answer('Действия отменены', reply_markup=ADMIN_KB)


#  Вернуться на шаг назад (на прошлое состояние)
@admin_router.message(StateFilter('*'), Command('назад'))
@admin_router.message(StateFilter('*'), F.text.casefold() == 'назад')
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state == AddProduct.name:
        await message.answer('Придыдущего шага нет, или введите название товара или напишите "отмена"')
        return

    previous = None
    for step in AddProduct.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f'ок, вы вернулись к прошлому шагу \n {AddProduct.texts[previous.state]}')
            return
        previous = step


#  Ловим данные для состояния name и потом меняем состояние на discription
@admin_router.message(AddProduct.name, or_f(F.text, F.text == '.'))
async def add_name(message: types.Message, state: FSMContext):
    #  Здесь можно сделать какую либо дополнительную проверку
    #  и выйти из хендлера не меняя состояние с отправки соответствующего сообшения
    #  например:

    # if len(message.text) >= 100:
    #     await message.answer(f'Название товара не должно привышать 100 символов \n Введите заново')
    #     return
    #
    # await state.update_data(name=message.text)
    # await message.answer('Введите описание товара')
    # await state.set_state(AddProduct.description)

    if message.text == '.':
        await state.update_data(name=AddProduct.product_for_change.name)
    else:
        #  Здесь можно сделать какую либо дополнительную проверку
        #  и выйти из хендлера не меняя состояние с отправки соответствующего сообшения
        #  например:
        if len(message.text) >= 100:
            await message.answer(
                'Название товара не должно привышать 100 символов \n Введите заново'
            )
            return

        await state.update_data(name=message.text)
    await message.answer('Введите описание товара')
    await state.set_state(AddProduct.description)


#  Хендлер для отловки некоректных вводов для состояния name
@admin_router.message(AddProduct.name)
async def add_name(message: types.Message, state: FSMContext):
    await message.answer('Вы ввели некоректные данные, введите текст названия товара')


#  Ловим данные для состояния description и потом меняем состояние на price
@admin_router.message(AddProduct.description, or_f(F.text, F.text == '.'))
async def add_description(message: types.Message, state: FSMContext):
    if message.text == '.':
        await state.update_data(description=AddProduct.product_for_change.description)
    else:
        await state.update_data(description=message.text)

    # await state.update_data(description=message.text)
    await message.answer('Введите стоимость товара')
    await state.set_state(AddProduct.price)


#  Хендлер для отловки некоректных вводов для состояния description
@admin_router.message(AddProduct.description)
async def add_description(message: types.Message, state: FSMContext):
    await message.answer('Вы ввели некоректные данные, введите текст заново')


#  Ловим данные для состояния pricr и потом меняем состояние на image
@admin_router.message(AddProduct.price, or_f(F.text, F.text == '.'))
async def add_price(message: types.Message, state: FSMContext):
    # try:
    #     float(message.text)
    # except ValueError:
    #     await message.answer('Введите коректное значение цены')
    #     return
    if message.text == '.':
        await state.update_data(price=AddProduct.product_for_change.price)
    else:
        try:
            float(message.text)
        except ValueError:
            await message.answer('Введите коректное значение цены')
            return
        await state.update_data(price=message.text)

    # await state.update_data(price=message.text)
    await message.answer('Загрузите изображение товара')
    await state.set_state(AddProduct.image)


#  Хендлер для отловки некоректных вводов для состояния image
@admin_router.message(AddProduct.price)
async def add_price(message: types.Message, state: FSMContext):
    await message.answer('Вы ввели некоректные данные, введите текст заново')


# Ловим данные для состояния image и потом выводим из состояния
@admin_router.message(AddProduct.image, or_f(F.photo, F.text == '.'))
# async def add_image(message: types.Message, state: FSMContext):
async def add_image(message: types.Message, state: FSMContext, session: AsyncSession()):
    # await state.update_data(image=message.photo[-1].file_id)  #второе изменение
    # await message.answer('Товар добавлен', reply_markup=ADMIN_KB)

    if message.text and message.text == '.':  # третье изменение (вставляем проверку)
        await state.update_data(image=AddProduct.product_for_change.image)
    else:
        await state.update_data(image=message.photo[-1].file_id)

    data = await state.get_data()
    # await message.answer(str(data))

    try:
        if AddProduct.product_for_change:
            await orm_update_product(session, AddProduct.product_for_change.id, data)
        else:
            await orm_add_product(session, data)
        await message.answer('Товар добавлен/изменен', reply_markup=ADMIN_KB)
        await state.clear()

    except Exception as e:
        await message.answer(
            f'Ошибка: \n{str(e)}\nОбратитесь к програмисту он опять денег хочет', reply_markup=ADMIN_KB
        )
        await state.clear()

    AddProduct.product_for_change = None


@admin_router.message(AddProduct.image)
async def add_image(message: types.Message, state: FSMContext):
    await message.answer('Отправьте фото пиши')
