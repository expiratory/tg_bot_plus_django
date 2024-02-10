import asyncio
import logging
from aiogram import Bot, Dispatcher
from os import getenv
from dotenv import load_dotenv, find_dotenv
import start_menu, goods, cart, categories, subcategories, faq, orders


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
        orders.router
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
