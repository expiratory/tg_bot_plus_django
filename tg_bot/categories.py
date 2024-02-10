from aiogram import types, F, Router
from db import connect_to_db, close_db
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton


router = Router()


@router.message(F.text.lower() == "каталог")
async def catalog(message: types.Message):
    await categories(message)


async def categories(message: types.Message):
    cursor, conn = await connect_to_db()
    cursor.execute('SELECT id, name FROM public.categories_category')
    records = cursor.fetchall()
    await close_db(cursor, conn)
    if len(records) == 0:
        await message.answer(text="Категорий пока не существует :(")

    buttons_list = []
    for item in records:
        category_id = item[0]
        category_name = item[1]
        buttons_list.append([types.InlineKeyboardButton(
            text=category_name,
            callback_data=f'Категория {str(category_id)}')]
        )
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons_list)
    await message.answer(
        "Нажмите на кнопку, чтобы перейти к категории",
        reply_markup=kb
    )
