from aiogram import types, F, Router, Bot
from aiogram.types import LabeledPrice, PreCheckoutQuery
from db import connect_to_db, close_db
from os import getenv
from dotenv import load_dotenv, find_dotenv


router = Router()
load_dotenv(find_dotenv())
UKASSA_TOKEN = getenv('UKASSA_TOKEN')


@router.message(F.text.lower() == "проверить баланс")
async def check_balance(message: types.Message):
    user_name = message.chat.username

    cursor, conn = await connect_to_db()
    cursor.execute(f"SELECT balance FROM public.user_user WHERE user_tg_nickname = '{user_name}'")
    records = cursor.fetchall()

    if len(records) == 0:
        cursor.execute(
            f"INSERT INTO public.user_user (user_tg_nickname, balance) values ('{user_name}', 0)"
        )
        conn.commit()
        balance = 0
    else:
        balance = records[0][0]

    await close_db(cursor, conn)
    await message.answer(text=f'Ваш баланс составляет {balance} руб.')


@router.message(F.text.lower() == "пополнить баланс")
async def add_balance(message: types.Message):
    from main import bot

    await bot.send_invoice(
        chat_id=message.from_user.id,
        title='Пополнить баланс',
        description='Пополнение баланса',
        provider_token=UKASSA_TOKEN,
        payload='add balance',
        currency='rub',
        prices=[
            LabeledPrice(
                label='Пополнить баланс на 1000 руб.',
                amount=100000
            )
        ],
        start_parameter='django_bot',
        provider_data=None,
        need_name=False,
        need_phone_number=False,
        need_email=False,
        need_shipping_address=False,
        is_flexible=False,
        disable_notification=False,
        protect_content=False,
        reply_to_message_id=None,
        reply_markup=None,
        request_timeout=60
    )


@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

    user_name = pre_checkout_query.from_user.username

    cursor, conn = await connect_to_db()
    cursor.execute(f"SELECT balance FROM public.user_user WHERE user_tg_nickname = '{user_name}'")
    records = cursor.fetchall()

    if len(records) == 0:
        cursor.execute(
            f"INSERT INTO public.user_user (user_tg_nickname, balance) values ('{user_name}', 0)"
        )
        conn.commit()
        balance = 0
    else:
        balance = records[0][0]

    total_amount = int(pre_checkout_query.total_amount // 100)
    updated_balance = balance + total_amount

    cursor.execute(
        f"UPDATE public.user_user SET balance = {updated_balance} WHERE user_tg_nickname = '{user_name}'"
    )
    conn.commit()

    await close_db(cursor, conn)
    await bot.send_message(text=f'Ваш баланс успешно пополнен на {total_amount} руб. Теперь он составляет '
                                f'{updated_balance} руб.', chat_id=pre_checkout_query.from_user.id)
