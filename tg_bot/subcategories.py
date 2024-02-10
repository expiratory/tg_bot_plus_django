from aiogram import types, F, Router
from db import connect_to_db, close_db
from categories import categories
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton


router = Router()


@router.callback_query(F.data.startswith("Категория"))
async def subcategories(callback: types.CallbackQuery):
    category_id = int(callback.data.split()[1])
    cursor, conn = await connect_to_db()
    cursor.execute(f'SELECT id, name FROM public.subcategories_subcategory WHERE category_id = {category_id}')
    records = cursor.fetchall()
    await close_db(cursor, conn)

    if len(records) == 0:
        await callback.message.answer(text="Подкатегорий в выбранной категории пока не существует, выберите другую")
        await categories(callback.message)

    buttons_list = []
    for item in records:
        subcategory_id = item[0]
        subcategory_name = item[1]
        buttons_list.append([types.InlineKeyboardButton(
            text=subcategory_name,
            callback_data=f'Подкатегория {str(subcategory_id)}')]
        )
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons_list)
    await callback.message.edit_text(
        "Нажмите на кнопку, чтобы перейти к подкатегории",
        reply_markup=kb
    )
