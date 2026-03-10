import asyncio
from database.models import create_tables

asyncio.run(create_tables())
print("✅ Таблицы созданы!")
