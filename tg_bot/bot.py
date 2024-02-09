import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.filters.command import Command
from aiogram.types import FSInputFile
from os import getenv
from dotenv import load_dotenv, find_dotenv
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
import psycopg2
from aiogram.exceptions import TelegramBadRequest

load_dotenv(find_dotenv())

DJANGO_PROJECT_MEDIA_ROOT = getenv('DJANGO_PROJECT_MEDIA_ROOT')


async def connect_to_db():
    conn = psycopg2.connect(
        dbname=getenv('POSTGRES_DB'),
        user=getenv('POSTGRES_USER'),
        password=getenv('POSTGRES_PASSWORD'),
        host=getenv('POSTGRES_HOST')
    )
    cursor = conn.cursor()
    return cursor, conn


async def close_db(cursor, conn):
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
    chat_name = getenv('CHAT_NAME')
    user_id = message.from_user.id

    try:
        chat_member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        if chat_member.status == "member" or chat_member.status == "administrator" or chat_member.status == "creator":
            await message.answer("Вы подписаны на группу!")
            await menu(message)
        else:
            await message.answer(f"Вы не подписаны на группу. Пожалуйста, подпишитесь на {chat_name}")
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


async def get_or_create_user_cart(user_name):
    cursor, conn = await connect_to_db()

    cursor.execute(
        f"SELECT * FROM public.user_user WHERE user_tg_nickname = '{user_name}'")
    user_records = cursor.fetchall()

    if len(user_records) == 0:
        cursor.execute(
            f"INSERT INTO public.user_user (user_tg_nickname) values ('{user_name}')"
        )
        conn.commit()
        cursor.execute(
            f"SELECT * FROM public.user_user WHERE user_tg_nickname = '{user_name}'")
        user_records = cursor.fetchall()

    bd_user_id = user_records[0][0]

    cursor.execute(
        f"SELECT * FROM public.cart_cart WHERE user_id = {bd_user_id}")
    user_cart_records = cursor.fetchall()

    if len(user_cart_records) == 0:
        cursor.execute(
            f"INSERT INTO public.cart_cart (user_id) values ('{bd_user_id}')"
        )
        conn.commit()
        cursor.execute(
            f"SELECT * FROM public.cart_cart WHERE user_id = {bd_user_id}")
        user_cart_records = cursor.fetchall()

    await close_db(cursor, conn)

    return user_cart_records


@dp.message(F.text.lower() == "каталог")
async def catalog(message: types.Message):
    await categories(message)


async def check_cart(message: types.Message):
    user_name = message.chat.username
    user_cart = await get_or_create_user_cart(user_name)
    cart_id = user_cart[0][0]

    cursor, conn = await connect_to_db()
    cursor.execute(
        f"SELECT ccg.id, ccg.quantity, gg.name, gg.price, gg.quantity FROM public.cart_cartgood ccg JOIN public.goods_good gg ON ccg.good_id = gg.id WHERE ccg.cart_id = {cart_id}")
    user_cart_good_records = cursor.fetchall()
    await close_db(cursor, conn)

    cart_good_list = None

    if len(user_cart_good_records) != 0:
        cart_good_list = []
        for item in user_cart_good_records:
            cart_good_id = item[0]
            cart_good_quantity = item[1]
            good_name = item[2]
            good_price = item[3]
            good_quantity = item[4]
            result_price = cart_good_quantity * good_price
            cart_good_list.append(
                [cart_good_id, cart_good_quantity, good_name, good_price, result_price, good_quantity])

    return cart_good_list


@dp.message(F.text.lower() == "корзина")
async def cart(message: types.Message):
    cart_good_list = await check_cart(message)

    if cart_good_list is not None:
        buttons_list = []
        position = 1
        for item in cart_good_list:
            info_for_reply = f"{item[2]} стоимостью {item[3]} количеством {item[1]} - итого {item[4]}. У нас в наличии: {item[5]}"
            delete_cart_good = types.InlineKeyboardButton(
                text="Удалить из корзины", callback_data=f'Удалить {item[0]}'
            )
            buttons_list.append([delete_cart_good])
            kb = types.InlineKeyboardMarkup(inline_keyboard=[[delete_cart_good]])
            await message.answer(text=f'Позиция {position}: {info_for_reply}', reply_markup=kb)
            position += 1
    else:
        await message.answer(text='Ваша корзина пуста')


@dp.callback_query(F.data.startswith("Удалить"))
async def delete_cart_good(callback: types.CallbackQuery):
    cart_good_id = int(callback.data.split()[1])

    cursor, conn = await connect_to_db()
    cursor.execute(
        f"DELETE FROM public.cart_cartgood WHERE id = {cart_good_id}")
    conn.commit()
    await close_db(cursor, conn)

    await callback.message.answer(text='Товар успешно удален из корзины. Вот что у вас осталось в корзине:')
    await cart(callback.message)



# @dp.message(F.text.lower() == "faq")
# async def faq(message: types.Message):
#     pass


async def categories(message: types.Message):
    cursor, conn = await connect_to_db()
    cursor.execute('SELECT id, name FROM public.categories_category')
    records = cursor.fetchall()
    if len(records) == 0:
        await message.answer(text="Категорий пока не существует :(")
    await close_db(cursor, conn)

    buttons_list = []
    for item in records:
        buttons_list.append([types.InlineKeyboardButton(
            text=item[1],
            callback_data=f'Категория {str(item[0])}')]
        )
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons_list)
    await message.answer(
        "Нажмите на кнопку, чтобы перейти к категории",
        reply_markup=kb
    )


@dp.callback_query(F.data.startswith("Категория"))
async def subcategories(callback: types.CallbackQuery):
    category_id = int(callback.data.split()[1])
    cursor, conn = await connect_to_db()
    cursor.execute(f'SELECT id, name FROM public.subcategories_subcategory WHERE category_id = {category_id}')
    records = cursor.fetchall()
    if len(records) == 0:
        await callback.message.answer(text="Подкатегорий в выбранной категории пока не существует, выберите другую")
        await categories(callback.message)
    await close_db(cursor, conn)

    buttons_list = []
    for item in records:
        buttons_list.append([types.InlineKeyboardButton(
            text=item[1],
            callback_data=f'Подкатегория {str(item[0])}')]
        )
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons_list)
    await callback.message.edit_text(
        "Нажмите на кнопку, чтобы перейти к подкатегории",
        reply_markup=kb
    )


@dp.callback_query(F.data.startswith("Подкатегория"))
async def goods(callback: types.CallbackQuery, number: int=0, good_id: int=0):
    subcategory_id = int(callback.data.split()[1])
    cursor, conn = await connect_to_db()
    if number == 0 and good_id == 0:
        cursor.execute(f'SELECT id, description, image, quantity FROM public.goods_good WHERE subcategory_id = {subcategory_id} AND quantity != 0')
        records = cursor.fetchall()
        if len(records) == 0:
            await callback.message.answer(text="Товаров в выбранной подкатегории пока не существует ,выберите другую")
            await categories(callback.message)
    else:
        cursor.execute(
            f'SELECT id, description, image, quantity FROM public.goods_good WHERE id = {good_id} AND quantity >= {number}')
        records = cursor.fetchall()
        if len(records) == 0:
            await callback.message.answer(text="Вы пытаетесь добавить больше, чем у нас есть в наличии")
            await categories(callback.message)
    await close_db(cursor, conn)

    for item in records:
        quantity = []
        buttons_list = []
        minus = types.InlineKeyboardButton(text="➖", callback_data=f'Минус {item[0]} {number if number else 1}')
        sum = types.InlineKeyboardButton(
            text=f"{number if number else 1}", callback_data=f'Количество {item[0]} {number if number else 1}'
        )
        plus = types.InlineKeyboardButton(text=" ➕", callback_data=f'Плюс {item[0]} {number if number else 1}')
        quantity.append(minus)
        quantity.append(sum)
        quantity.append(plus)
        cart = [types.InlineKeyboardButton(
            text="Добавить в корзину",
            callback_data=f"Товар {item[0]} {number}"
        )]
        buttons_list.append(quantity)
        buttons_list.append(cart)
        kb = types.InlineKeyboardMarkup(inline_keyboard=buttons_list)
        image = FSInputFile(f"{DJANGO_PROJECT_MEDIA_ROOT}{item[2]}")

        if number == 0 and good_id == 0:
            await bot.send_photo(chat_id=callback.message.chat.id, photo=image, caption=item[1], reply_markup=kb)
        else:
            try:
                await bot.edit_message_reply_markup(reply_markup=kb, message_id= callback.message.message_id, chat_id=callback.message.chat.id)
            except TelegramBadRequest:
                pass


@dp.callback_query(F.data.startswith("Минус"))
async def minus(callback: types.CallbackQuery):
    number = int(callback.data.split()[2]) - 1 if int(callback.data.split()[2]) > 0 else 1
    good_id = int(callback.data.split()[1])
    await goods(callback, number, good_id)


@dp.callback_query(F.data.startswith("Плюс"))
async def plus(callback: types.CallbackQuery):
    number = int(callback.data.split()[2]) + 1
    good_id = int(callback.data.split()[1])
    await goods(callback, number, good_id)


@dp.callback_query(F.data.startswith("Товар"))
async def add_to_cart(callback: types.CallbackQuery):
    good_id = int(callback.data.split()[1])
    quantity = int(callback.data.split()[2])
    user_name = callback.message.chat.username
    user_cart = await get_or_create_user_cart(user_name)
    cart_id = user_cart[0][0]

    cursor, conn = await connect_to_db()
    cursor.execute(
        f"INSERT INTO public.cart_cartgood (quantity, cart_id, good_id) values ({quantity}, {cart_id}, {good_id})"
    )
    conn.commit()
    await close_db(cursor, conn)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
