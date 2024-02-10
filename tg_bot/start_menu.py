from aiogram import types, F, Router
from aiogram.filters.command import Command
from os import getenv
from dotenv import load_dotenv, find_dotenv
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton


load_dotenv(find_dotenv())
router = Router()


@router.message(F.text.lower() == "проверить подписку")
async def check_subscription(message: types.Message):
    from main import bot

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


@router.message(Command("start"))
async def start(message: types.Message):
    await check_subscription(message)


@router.message(Command("menu"))
async def menu(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="Каталог"),
            types.KeyboardButton(text="Корзина"),
            types.KeyboardButton(text="FAQ")
        ],
        [
            types.KeyboardButton(text="Пополнить баланс"),
            types.KeyboardButton(text="Проверить баланс")
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder='Выберите пункт меню',
    )
    await message.answer("Куда вы хотите перейти?", reply_markup=keyboard)
