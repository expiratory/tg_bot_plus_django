from aiogram import types, F, Router
from db import connect_to_db, close_db
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest
from os import getenv
from dotenv import load_dotenv, find_dotenv


router = Router()


@router.message(F.text.lower() == "каталог")
async def catalog(message: types.Message):
    await categories(message)


async def categories(message: types.Message, page: int=0, start: bool=True):
    cursor, conn = await connect_to_db()
    cursor.execute('SELECT id, name FROM public.categories_category')
    records = cursor.fetchall()
    await close_db(cursor, conn)
    if len(records) == 0:
        await message.answer(text="Категорий пока не существует :(")

    buttons_list = []
    page_size = int(getenv('GLOBAL_PAGINATION_PAGE_SIZE'))
    number = page * page_size

    for i in range(page_size):
        try:
            category_id = records[number+i][0]
            category_name = records[number+i][1]
            buttons_list.append([types.InlineKeyboardButton(
                text=category_name,
                callback_data=f'Категория {str(category_id)}')]
            )
        except IndexError:
            pass

    if len(buttons_list) != 0:
        buttons_list.append([
            types.InlineKeyboardButton(
                text='Назад',
                callback_data=f'Назад {page} {start} категории'
            ),
            types.InlineKeyboardButton(
                text='Далее',
                callback_data=f'Далее {page} {start} категории'
            )
        ])
        kb = types.InlineKeyboardMarkup(inline_keyboard=buttons_list)

        if start:
            await message.answer(
                "Нажмите на кнопку, чтобы перейти к категории",
                reply_markup=kb
            )
        else:
            try:
                await message.edit_reply_markup(
                    reply_markup=kb
                )
            except TelegramBadRequest:
                pass
