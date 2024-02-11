from aiogram import types, F, Router
from db import connect_to_db, close_db
from os import getenv
from dotenv import load_dotenv, find_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart



load_dotenv(find_dotenv())
router = Router()


async def send_email_for_admin(bd_user_id, user_order_id, time_now_for_db, order_item_list):
    try:
        cursor, conn = await connect_to_db()
        cursor.execute(
            f"SELECT user_tg_nickname FROM public.user_user WHERE id = {bd_user_id}"
        )
        user_tg_nickname = cursor.fetchone()[0]
        await close_db(cursor, conn)

        admin_email = getenv('EMAIL_ADMIN')
        email_sender_username = getenv('EMAIL_SENDER_USERNAME')
        email_sender_password = getenv('EMAIL_SENDER_PASSWORD')
        email_host = getenv('EMAIL_HOST')
        email_port = getenv('EMAIL_PORT')
        order_items = '\n'.join(f'{a} {b} {c}' for inner_array in order_item_list for a, b, c in [inner_array])
        title = 'Покупка в телеграм-боте.'
        content = (f'Пользователь @{user_tg_nickname} оформил заказ {user_order_id} в это время - '
                   f'{time_now_for_db}. Товары в заказе:\n{order_items}')
        type = 'Письмо для администратора'

        msg = MIMEMultipart()
        msg['From'] = email_sender_username
        msg['To'] = admin_email
        msg['Subject'] = title

        body = content
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP_SSL(host=email_host, port=email_port)
        server.login(email_sender_username, email_sender_password)
        server.send_message(msg)
        server.quit()

        cursor, conn = await connect_to_db()
        cursor.execute(
            f"INSERT INTO public.emails_email (type, title, content, admin_email, created_at, order_id) "
            f"values ('{type}', '{title}', '{content}', '{admin_email}', '{time_now_for_db}', {user_order_id})"
        )
        conn.commit()
        await close_db(cursor, conn)
    except Exception as e:
        print(str(e))
