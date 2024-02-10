from aiogram import types, F, Router
from db import connect_to_db, close_db
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton


router = Router()


async def get_or_create_user_cart(user_name):
    cursor, conn = await connect_to_db()

    cursor.execute(
        f"SELECT * FROM public.user_user WHERE user_tg_nickname = '{user_name}'")
    user_records = cursor.fetchall()

    if len(user_records) == 0:
        cursor.execute(
            f"INSERT INTO public.user_user (user_tg_nickname, balance) values ('{user_name}', 0)"
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


@router.message(F.text.lower() == "корзина")
async def cart(message: types.Message):
    cart_good_list = await check_cart(message)

    if cart_good_list is not None:
        buttons_list = []
        position = 1
        cart_sum = 0
        for item in cart_good_list:
            cart_good_id = item[0]
            result_price = item[4]
            good_name = item[2]
            good_price = item[3]
            cart_good_quantity = item[1]
            good_quantity = item[5]

            cart_sum += result_price
            info_for_reply = (f"{good_name} стоимостью {good_price} количеством {cart_good_quantity} - итого {result_price}. "
                              f"У нас в наличии: {good_quantity}")
            delete_cart_good = types.InlineKeyboardButton(
                text="Удалить из корзины", callback_data=f'Удалить {cart_good_id}'
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


@router.callback_query(F.data.startswith("Удалить"))
async def delete_cart_good(callback: types.CallbackQuery):
    cart_good_id = int(callback.data.split()[1])

    cursor, conn = await connect_to_db()
    cursor.execute(
        f"DELETE FROM public.cart_cartgood WHERE id = {cart_good_id}")
    conn.commit()
    await close_db(cursor, conn)

    await callback.message.answer(text='Товар успешно удален из корзины. Вот что у вас осталось в корзине:')
    await cart(callback.message)


@router.callback_query(F.data.startswith("Товар"))
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
