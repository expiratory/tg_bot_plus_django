import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.filters.command import Command
from os import getenv
from dotenv import load_dotenv, find_dotenv
from aiogram.utils.keyboard import InlineKeyboardBuilder

load_dotenv(find_dotenv())

logging.basicConfig(level=logging.DEBUG, filename='logs', format=' %(asctime)s - %(levelname)s - %(message)s')

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


@dp.message(F.text.lower() == "корзина")
async def cart(message: types.Message):
    pass


@dp.message(F.text.lower() == "faq")
async def faq(message: types.Message):
    pass


async def categories(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Одежда",
        callback_data="clothes")
    )
    builder.add(types.InlineKeyboardButton(
        text="Обувь",
        callback_data="shoes")
    )
    await message.answer(
        "Нажмите на кнопку, чтобы перейти к подкатегории",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data == "clothes")
async def open_clothes(callback: types.CallbackQuery):
    await callback.answer()
    await clothes(callback.message)


@dp.callback_query(F.data == "shoes")
async def open_shoes(callback: types.CallbackQuery):
    await callback.answer()
    await shoes(callback.message)


async def clothes(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Футболки",
        callback_data="t_shirts")
    )
    builder.add(types.InlineKeyboardButton(
        text="Джинсы",
        callback_data="jeans")
    )
    await message.answer(
        "Нажмите на кнопку, чтобы перейти к товарам",
        reply_markup=builder.as_markup()
    )


async def shoes(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Кроссовки",
        callback_data="sneakers")
    )
    builder.add(types.InlineKeyboardButton(
        text="Сапоги",
        callback_data="boots")
    )
    await message.answer(
        "Нажмите на кнопку, чтобы перейти к товарам",
        reply_markup=builder.as_markup()
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
