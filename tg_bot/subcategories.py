from aiogram import types, F, Router
from db import connect_to_db, close_db
from categories import categories
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest
from os import getenv
from dotenv import load_dotenv, find_dotenv


router = Router()


@router.callback_query(F.data.startswith("Категория"))
async def subcategories(callback: types.CallbackQuery, page: int=0, start: bool=True, category_id: int=None):
    if category_id is None:
        category_id = int(callback.data.split()[1])
    cursor, conn = await connect_to_db()
    cursor.execute(f'SELECT id, name FROM public.subcategories_subcategory WHERE category_id = {category_id}')
    records = cursor.fetchall()
    await close_db(cursor, conn)

    if len(records) == 0:
        await callback.message.answer(text="Подкатегорий в выбранной категории пока не существует, выберите другую")
        await categories(callback.message)

    buttons_list = []
    page_size = int(getenv('GLOBAL_PAGINATION_PAGE_SIZE'))
    number = page * page_size

    for i in range(page_size):
        try:
            subcategory_id = records[number+i][0]
            subcategory_name = records[number+i][1]
            buttons_list.append([types.InlineKeyboardButton(
                text=subcategory_name,
                callback_data=f'Подкатегория {str(subcategory_id)}')]
            )
        except IndexError:
            pass

    if len(buttons_list) != 0:
        buttons_list.append([
            types.InlineKeyboardButton(
                text='Назад',
                callback_data=f'Назад {page} {start} подкатегории {category_id}'
            ),
            types.InlineKeyboardButton(
                text='Далее',
                callback_data=f'Далее {page} {start} подкатегории {category_id}'
            )
        ])
        kb = types.InlineKeyboardMarkup(inline_keyboard=buttons_list)

        if start:
            await callback.message.answer(
                "Нажмите на кнопку, чтобы перейти к подкатегории",
                reply_markup=kb
            )
        else:
            try:
                await callback.message.edit_reply_markup(
                    reply_markup=kb
                )
            except TelegramBadRequest:
                pass

@router.callback_query(F.data.startswith("Назад"))
async def backward(callback: types.CallbackQuery):
    category = callback.data.split()[3] == 'категории'
    subcategory = callback.data.split()[3] == 'подкатегории'
    start = callback.data.split()[2]
    if start:
        start = False
    page = int(callback.data.split()[1]) - 1 if int(callback.data.split()[1]) > 0 else 0
    if category:
        await categories(callback.message, page, start)
    if subcategory:
        category_id = callback.data.split()[4]
        await subcategories(callback, page, start, category_id)


@router.callback_query(F.data.startswith("Далее"))
async def forward(callback: types.CallbackQuery):
    category = callback.data.split()[3] == 'категории'
    subcategory = callback.data.split()[3] == 'подкатегории'
    start = callback.data.split()[2]
    if start:
        start = False
    page = int(callback.data.split()[1]) + 1
    if category:
        await categories(callback.message, page, start)
    if subcategory:
        category_id = callback.data.split()[4]
        await subcategories(callback, page, start, category_id)
