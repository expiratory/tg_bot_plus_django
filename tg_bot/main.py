import asyncio
import logging
from aiogram import Bot, Dispatcher
from os import getenv
from dotenv import load_dotenv, find_dotenv
import start_menu
import goods
import cart
import categories
import subcategories
import faq
import orders
import user_balance


load_dotenv(find_dotenv())

# logging.basicConfig(level=logging.DEBUG, filename='logs', format=' %(asctime)s - %(levelname)s - %(message)s')  # prod
logging.basicConfig(level=logging.INFO)  # dev

bot = Bot(token=getenv('BOT_TOKEN'))

async def main():
    dp = Dispatcher()
    dp.include_routers(
        start_menu.router,
        goods.router,
        cart.router,
        subcategories.router,
        categories.router,
        faq.router,
        orders.router,
        user_balance.router
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
