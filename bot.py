import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database.models import create_tables
from handlers import start

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Подключаем хендлеры
    dp.include_router(start.router)

    # Создаём таблицы при запуске
    await create_tables()

    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())