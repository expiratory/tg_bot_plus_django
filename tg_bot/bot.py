import asyncio
import logging
from datetime import datetime

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
        f"SELECT ccg.id, ccg.quantity, gg.name, gg.price, gg.quantity, gg.id, ccg.cart_id FROM public.cart_cartgood "
        f"ccg JOIN public.goods_good gg ON ccg.good_id = gg.id WHERE ccg.cart_id = {cart_id}")
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
            good_id = item[5]
            cart_id = item[6]
            result_price = cart_good_quantity * good_price
            cart_good_list.append(
                [cart_good_id, cart_good_quantity, good_name, good_price, result_price, good_quantity, good_id, cart_id])

    return cart_good_list


@dp.message(F.text.lower() == "корзина")
async def cart(message: types.Message):
    cart_good_list = await check_cart(message)

    if cart_good_list is not None:
        buttons_list = []
        position = 1
        cart_sum = 0
        for item in cart_good_list:
            cart_sum += item[4]
            info_for_reply = (f"{item[2]} стоимостью {item[3]} количеством {item[1]} - итого {item[4]}. "
                              f"У нас в наличии: {item[5]}")
            delete_cart_good = types.InlineKeyboardButton(
                text="Удалить из корзины", callback_data=f'Удалить {item[0]}'
            )
            buttons_list.append([delete_cart_good])
            kb = types.InlineKeyboardMarkup(inline_keyboard=[[delete_cart_good]])
            await message.answer(text=f'Позиция {position}: {info_for_reply}', reply_markup=kb)
            position += 1
        await message.answer(
            text=f'Сумма корзины: {cart_sum}. Если вы готовы сделать заказ, введите данные для доставки. '
                 f'ОБЯЗАТЕЛЬНО начните свое сообщение со слов "Данные для доставки"'
        )
    else:
        await message.answer(text='Ваша корзина пуста')


@dp.message(F.text.lower().startswith('данные для доставки'))
async def get_post_data_and_make_order(message: types.Message):
    post_data = message.text
    check_post_data = post_data.split()[3:]

    if check_post_data:
        post_data = ' '.join(check_post_data)
        cart_good_list = await check_cart(message)

        if cart_good_list is not None:
            check_quantity = True

            for item in cart_good_list:
                cursor, conn = await connect_to_db()
                cursor.execute(f'SELECT quantity FROM public.goods_good WHERE id = {item[6]}')
                record = cursor.fetchall()
                await close_db(cursor, conn)

                real_quantity = record[0][0]

                if real_quantity < item[6]:
                    await message.answer(text=f'Товара {item[2]} осталось меньше, чем у вас в корзине, сейчас в '
                                              f'наличии {real_quantity} шт. Перейдите в корзину, удалите товар и '
                                              f'закажите возможное количество.')
                    check_quantity = False

            if check_quantity:
                cart_id = cart_good_list[0][7]

                cursor, conn = await connect_to_db()
                cursor.execute(f'SELECT user_id FROM public.cart_cart WHERE id = {cart_id}')
                record = cursor.fetchall()
                await close_db(cursor, conn)

                bd_user_id = record[0][0]
                str_time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                time_now_for_db = str_time_now + '+00'

                cursor, conn = await connect_to_db()
                cursor.execute(
                    f"INSERT INTO public.orders_order (created_at, user_id, post_data) values "
                    f"('{str_time_now}', {bd_user_id}, '{post_data}')")
                conn.commit()
                cursor.execute(
                    f"SELECT id FROM public.orders_order WHERE created_at = '{time_now_for_db}' AND "
                    f"user_id = '{bd_user_id}'"
                )
                user_order_id = cursor.fetchall()[0][0]
                await close_db(cursor, conn)

                for item in cart_good_list:
                    cursor, conn = await connect_to_db()
                    cursor.execute(
                        f"INSERT INTO public.orders_orderitem (quantity, good_id, order_id) values "
                        f"('{item[5]}', {item[6]}, '{user_order_id}')")
                    conn.commit()
                    await close_db(cursor, conn)

                await message.answer(text='Заказ успешно создан!')
        else:
            await message.answer(text='Ваша корзина пуста')

    else:
        await message.answer(text='Данные для доставки не были введены')


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


@dp.message(F.text.lower() == "faq")
async def faq(message: types.Message):
    cursor, conn = await connect_to_db()
    cursor.execute(f"SELECT id, question, answer FROM public.faq_faq")
    records = cursor.fetchall()
    await close_db(cursor, conn)

    if len(records) == 0:
        await message.answer(text="Раздела FAQ пока не существует :(")
    else:
        buttons_list = []

        for item in records:
            question = item[1]
            answer_id = item[0]

            question_button = [types.InlineKeyboardButton(
                text=question,
                callback_data=f"Ответ {str(answer_id)}"
            )]
            buttons_list.append(question_button)
        kb = types.InlineKeyboardMarkup(inline_keyboard=buttons_list)
        await message.answer(text='Вот список частозадаваемых вопросов:', reply_markup=kb)


@dp.callback_query(F.data.startswith("Ответ"))
async def get_faq_answer(callback: types.CallbackQuery):
    answer_id = callback.data.split()[1]
    cursor, conn = await connect_to_db()
    cursor.execute(f"SELECT question, answer FROM public.faq_faq WHERE id = {answer_id}")
    record = cursor.fetchall()
    await close_db(cursor, conn)
    question = record[0][0]
    answer = record[0][1]
    reply_message = f'Вот ответ на вопрос {question}: {answer}'
    await callback.message.answer(text=reply_message)



async def categories(message: types.Message):
    cursor, conn = await connect_to_db()
    cursor.execute('SELECT id, name FROM public.categories_category')
    records = cursor.fetchall()
    await close_db(cursor, conn)
    if len(records) == 0:
        await message.answer(text="Категорий пока не существует :(")

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
    await close_db(cursor, conn)

    if len(records) == 0:
        await callback.message.answer(text="Подкатегорий в выбранной категории пока не существует, выберите другую")
        await categories(callback.message)

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
            await bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=image,
                caption=f'{item[1]}. В наличии: {item[3]}',
                reply_markup=kb
            )
        else:
            try:
                await bot.edit_message_reply_markup(
                    reply_markup=kb,
                    message_id= callback.message.message_id,
                    chat_id=callback.message.chat.id
                )
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
