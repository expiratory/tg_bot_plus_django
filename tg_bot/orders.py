from datetime import datetime
from aiogram import types, F, Router
from db import connect_to_db, close_db
from cart import check_cart


router = Router()


@router.message(F.text.lower().startswith('данные для доставки'))
async def get_post_data_and_make_order(message: types.Message):
    post_data = message.text
    check_post_data = post_data.split()[3:]

    if check_post_data:
        post_data = ' '.join(check_post_data)
        cart_good_list = await check_cart(message)

        if cart_good_list is not None:
            check_quantity = True

            for item in cart_good_list:
                good_id = item[6]
                cursor, conn = await connect_to_db()
                cursor.execute(f'SELECT quantity FROM public.goods_good WHERE id = {good_id}')
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
                cursor.execute(f"SELECT balance FROM public.user_user WHERE id = {bd_user_id}")
                records = cursor.fetchall()
                balance = records[0][0]
                await close_db(cursor, conn)

                order_item_counter = 0

                for item in cart_good_list:
                    cart_good_quantity = item[1]
                    good_id = item[6]
                    good_quantity = item[5]
                    good_price = item[3]
                    cart_good_id = item[0]

                    order_item_price = good_price * cart_good_quantity
                    if balance < order_item_price:
                        await message.answer(text='У вас недостаточно денег для оплаты этого товара :(')
                    else:
                        cursor, conn = await connect_to_db()
                        cursor.execute(
                            f"INSERT INTO public.orders_orderitem (quantity, good_id, order_id) values "
                            f"('{cart_good_quantity}', {good_id}, '{user_order_id}')")
                        conn.commit()
                        cursor.execute(
                            f"SELECT id FROM public.orders_orderitem WHERE quantity = '{cart_good_quantity}' AND "
                            f"good_id = {good_id} AND order_id = '{user_order_id}'")
                        order_item_id = cursor.fetchall()[0][0]
                        new_quantity = good_quantity - cart_good_quantity
                        cursor.execute(
                            f"UPDATE public.goods_good SET quantity = {new_quantity}  WHERE id = {good_id}"
                        )
                        conn.commit()
                        updated_balance = balance - order_item_price
                        cursor.execute(
                            f"UPDATE public.user_user SET balance = {updated_balance} WHERE id = {bd_user_id}"
                        )
                        conn.commit()
                        cursor.execute(
                            f"DELETE FROM public.cart_cartgood WHERE id = {cart_good_id}"
                        )
                        conn.commit()
                        await close_db(cursor, conn)
                        await message.answer(text=f'Успешно оплачена позиция с номером {order_item_id} заказа номер '
                                                  f'{user_order_id}!')
                        order_item_counter += 1

                if order_item_counter == 0:
                    cursor, conn = await connect_to_db()
                    cursor.execute(
                        f"DELETE FROM public.orders_order WHERE id = {user_order_id}"
                    )
                    conn.commit()
                    await close_db(cursor, conn)
                    await message.answer(text='К сожалению, у вас недостаточно денег для оплаты позиций вашего заказа. '
                                              'Пополните баланс и попробуйте снова.')
        else:
            await message.answer(text='Ваша корзина пуста')

    else:
        await message.answer(text='Данные для доставки не были введены')
