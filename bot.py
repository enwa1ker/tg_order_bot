import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database.models import create_tables
from handlers import start, order

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(order.router)

    await create_tables()

    # Короче, добавить в bot.py в функцию main() после create_tables():
    from utils.sheets import init_sheets
    init_sheets()

    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
