from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from filters.chat_types import ChatTypesFilter, IsAdmin
from kbds.reply import get_keyboard

admin_router = Router()
admin_router.message.filter(ChatTypesFilter(['private']), IsAdmin())

ADMIN_KB = get_keyboard(
    'Добавить товар',
    'Изменить товар',
    'Удалить товар',
    'Я так, просто посмотреть зашел',
    placeholder='Выберите действие',
    sizes=(2, 1, 1),
)


@admin_router.message(Command('admin'))
async def add_product(message: types.Message):
    await message.answer('Что хотите сделать?', reply_markup=ADMIN_KB)


@admin_router.message(F.text == 'Я так, просто посмотреть зашел')
async def starting_at_product(message: types.Message):
    await message.answer('Ок, вот список товаров')


@admin_router.message(F.text == 'Изменить товар')
async def change_product(message: types.Message):
    await message.answer('Ок, вот список товаров')


@admin_router.message(F.text == 'Удалить товар')
async def delete_product(message: types.Message):
    await message.answer('Выберите товар(ы) для удаления')


#  Код ниже для машины состояний (FSM)

class AddProduct(StatesGroup):
    # шаги состояния
    name = State()
    description = State()
    price = State()
    image = State()

    texts = {
        'AddProduct:name': 'Введите название заново',
        'AddProduct:description': 'Введите описание заново',
        'AddProduct:price': 'Введите стоимость заново',
        'AddProduct:image': 'Этот стейт последний))',

    }


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
@admin_router.message(AddProduct.name, F.text)
async def add_name(message: types.Message, state: FSMContext):
    #  Здесь можно сделать какую либо дополнительную проверку
    #  и выйти из хендлера не меняя состояние с отправки соответствующего сообшения
    #  например:
    if len(message.bot) >= 100:
        await message.answer(f'Название товара не должно привышать 100 символов \n Введите заново')
        return

    await state.update_data(name=message.text)
    await message.answer('Введите описание товара')
    await state.set_state(AddProduct.description)


#  Хендлер для отловки некоректных вводов для состояния name
@admin_router.message(AddProduct.name)
async def add_name(message: types.Message):
    await message.answer('Вы ввели некоректные данные, введите текст названия товара')


#  Ловим данные для состояния description и потом меняем состояние на price
@admin_router.message(AddProduct.description, F.text)
async def add_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer('Введите стоимость товара')
    await state.set_state(AddProduct.price)


#  Хендлер для отловки некоректных вводов для состояния description
@admin_router.message(AddProduct.description)
async def add_name(message: types.Message):
    await message.answer('Вы ввели некоректные данные, введите текст заново')


#  Ловим данные для состояния pricr и потом меняем состояние на image
@admin_router.message(AddProduct.price, F.text)
async def add_price(message: types.Message, state: FSMContext):
    try:
        float(message.text)
    except ValueError:
        await message.answer('Введите коректное значение цены')
        return

    await state.update_data(price=message.text)
    await message.answer('Загрузите изображение товара')
    await state.set_state(AddProduct.image)


#  Хендлер для отловки некоректных вводов для состояния image
@admin_router.message(AddProduct.price)
async def add_price(message: types.Message):
    await message.answer('Вы ввели некоректные данные, введите текст заново')


# Ловим данные для состояния image и потом выводим из состояния
@admin_router.message(AddProduct.image, F.photo)
async def add_image(message: types.Message, state: FSMContext):
    await state.update_data(image=message.photo[-1].file_id)
    await message.answer('Товар добавлен', reply_markup=ADMIN_KB)
    data = await state.get_data()
    await message.answer(str(data))
    await state.clear()


@admin_router.message(AddProduct.image)
async def add_image(message: types.Message):
    await message.answer('Отправьте фото пиши')
