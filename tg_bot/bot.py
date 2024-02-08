import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.filters.command import Command
from os import getenv
from dotenv import load_dotenv, find_dotenv
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
import psycopg2

load_dotenv(find_dotenv())


def connect_to_db():
    conn = psycopg2.connect(
        dbname=getenv('POSTGRES_DB'),
        user=getenv('POSTGRES_USER'),
        password=getenv('POSTGRES_PASSWORD'),
        host=getenv('POSTGRES_HOST')
    )
    cursor = conn.cursor()
    return cursor, conn


def close_db(cursor, conn):
    cursor.close()
    conn.close()


# logging.basicConfig(level=logging.DEBUG, filename='logs', format=' %(asctime)s - %(levelname)s - %(message)s')  # prod
logging.basicConfig(level=logging.INFO)  # dev

bot = Bot(token=getenv('BOT_TOKEN'))

dp = Dispatcher()

router = Router()


@dp.message(F.text.lower() == "проверить подписку")
async def check_subscription(message: types.Message):
    chat_id = getenv('CHAT_ID')
    user_id = message.from_user.id

    try:
        chat_member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        if chat_member.status == "member" or chat_member.status == "administrator" or chat_member.status == "creator":
            await message.answer("Вы подписаны на группу!")
            await menu(message)
        else:
            await message.answer("Вы не подписаны на группу. Пожалуйста, подпишитесь на @chat_name.")
            kb = [
                [types.KeyboardButton(text="Проверить подписку")]
            ]
            keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
            await message.answer(
                "После того, как вы подпишитесь на группу, нажмите на кнопку 'Проверить подписку'.",
                reply_markup=keyboard
            )

    except Exception as e:
        await message.answer(f"Ошибка: {e}")


@dp.message(Command("start"))
async def start(message: types.Message):
    await check_subscription(message)


@dp.message(Command("menu"))
async def menu(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="Каталог"),
            types.KeyboardButton(text="Корзина"),
            types.KeyboardButton(text="FAQ")
         ]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder='Выберите пункт меню',
    )
    await message.answer("Куда вы хотите перейти?", reply_markup=keyboard)


@dp.message(F.text.lower() == "каталог")
async def catalog(message: types.Message):
    await categories(message)


# @dp.message(F.text.lower() == "корзина")
# async def cart(message: types.Message):
#     pass
#
#
# @dp.message(F.text.lower() == "faq")
# async def faq(message: types.Message):
#     pass


async def categories(message: types.Message):
    cursor, conn = connect_to_db()
    cursor.execute('SELECT id, name FROM public.categories_category')
    records = cursor.fetchall()
    close_db(cursor, conn)

    buttons_list = []
    for item in records:
        buttons_list.append([types.InlineKeyboardButton(
            text=item[1],
            callback_data=f'Категория {str(item[0])}')]
        )
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons_list)
    await message.answer(
        "Нажмите на кнопку, чтобы перейти к подкатегории",
        reply_markup=kb
    )


@dp.callback_query(F.data == "clothes")
async def open_clothes(callback: types.CallbackQuery):
    await callback.answer()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
