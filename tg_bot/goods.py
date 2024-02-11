from aiogram import types, F, Router
from aiogram.types import FSInputFile
from aiogram.exceptions import TelegramBadRequest
from db import connect_to_db, close_db
from categories import categories
from os import getenv
from dotenv import load_dotenv, find_dotenv
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton



load_dotenv(find_dotenv())
router = Router()
DJANGO_PROJECT_MEDIA_ROOT = getenv('DJANGO_PROJECT_MEDIA_ROOT')


@router.callback_query(F.data.startswith("Подкатегория"))
async def goods(callback: types.CallbackQuery, number: int=0, good_id: int=0):
    from main import bot

    subcategory_id = int(callback.data.split()[1])
    cursor, conn = await connect_to_db()
    if number == 0 and good_id == 0:
        cursor.execute(f'SELECT id, description, image, quantity FROM public.goods_good '
                       f'WHERE subcategory_id = {subcategory_id} AND quantity != 0')
        records = cursor.fetchall()
        if len(records) == 0:
            await callback.message.answer(text="Товаров в выбранной подкатегории пока не существует ,выберите другую")
            await categories(callback.message)
    else:
        cursor.execute(
            f'SELECT id, description, image, quantity FROM public.goods_good '
            f'WHERE id = {good_id} AND quantity >= {number}')
        records = cursor.fetchall()
        if len(records) == 0:
            await callback.message.answer(text="Вы пытаетесь добавить больше, чем у нас есть в наличии")
            await categories(callback.message)
    await close_db(cursor, conn)

    for item in records:
        id_good = item[0]
        good_description = item[1]
        good_image = item[2]
        good_quantity = item[3]

        quantity = []
        buttons_list = []
        minus = types.InlineKeyboardButton(text="➖", callback_data=f'Минус {id_good} {number if number else 1}')
        sum = types.InlineKeyboardButton(
            text=f"{number if number else 1}", callback_data=f'Количество {id_good} {number if number else 1}'
        )
        plus = types.InlineKeyboardButton(text=" ➕", callback_data=f'Плюс {id_good} {number if number else 1}')
        quantity.append(minus)
        quantity.append(sum)
        quantity.append(plus)
        cart = [types.InlineKeyboardButton(
            text="Добавить в корзину",
            callback_data=f"Товар {id_good} {number if number else 1}"
        )]
        buttons_list.append(quantity)
        buttons_list.append(cart)
        kb = types.InlineKeyboardMarkup(inline_keyboard=buttons_list)
        image = FSInputFile(f"{DJANGO_PROJECT_MEDIA_ROOT}{good_image}")

        if number == 0 and good_id == 0:
            await bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=image,
                caption=f'{good_description}. В наличии: {good_quantity} шт.',
                reply_markup=kb
            )
        else:
            try:
                await bot.edit_message_reply_markup(
                    reply_markup=kb,
                    message_id=callback.message.message_id,
                    chat_id=callback.message.chat.id
                )
            except TelegramBadRequest:
                pass


@router.callback_query(F.data.startswith("Минус"))
async def minus(callback: types.CallbackQuery):
    number = int(callback.data.split()[2]) - 1 if int(callback.data.split()[2]) > 0 else 1
    good_id = int(callback.data.split()[1])
    await goods(callback, number, good_id)


@router.callback_query(F.data.startswith("Плюс"))
async def plus(callback: types.CallbackQuery):
    number = int(callback.data.split()[2]) + 1
    good_id = int(callback.data.split()[1])
    await goods(callback, number, good_id)
