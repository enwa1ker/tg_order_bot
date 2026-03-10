import asyncio
import aiosqlite

DB_PATH = "bot.db"

async def seed():
    async with aiosqlite.connect(DB_PATH) as db:

        # Дистрибьюторы
        await db.executemany("""
            INSERT OR IGNORE INTO distributors (id, name, is_active, commission_percent)
            VALUES (?, ?, 1, 6.0)
        """, [
            (1, "Шоро"),
            (2, "Forester"),
            (3, "Абдыш-Ата"),
        ])

        # Категории
        await db.executemany("""
            INSERT OR IGNORE INTO categories (id, distributor_id, name, is_active)
            VALUES (?, ?, ?, 1)
        """, [
            (1, 1, "Напитки"),
            (2, 1, "Снеки"),
            (3, 2, "Напитки"),
            (4, 3, "Напитки"),
        ])

        # Подкатегории
        await db.executemany("""
            INSERT OR IGNORE INTO subcategories (id, category_id, name, is_active)
            VALUES (?, ?, ?, 1)
        """, [
            (1, 1, "Вода"),
            (2, 1, "Газированные напитки"),
            (3, 2, "Чипсы"),
            (4, 3, "Энергетики"),
            (5, 4, "Соки"),
        ])

        # Бренды
        await db.executemany("""
            INSERT OR IGNORE INTO brands (id, subcategory_id, name, is_active)
            VALUES (?, ?, ?, 1)
        """, [
            (1, 1, "Шоро"),
            (2, 2, "Шоро"),
            (3, 3, "Forester"),
            (4, 4, "Forester Energy"),
            (5, 5, "Абдыш-Ата"),
        ])

        # Товары
        await db.executemany("""
            INSERT OR IGNORE INTO products 
            (id, distributor_id, category_id, subcategory_id, brand_id, 
             name, unit_price, stock_status, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'in_stock', 1)
        """, [
            (1, 1, 1, 1, 1, "Шоро вода 1л", 25.0),
            (2, 1, 1, 1, 1, "Шоро вода 0.5л", 15.0),
            (3, 1, 1, 2, 2, "Максым 1л", 45.0),
            (4, 1, 1, 2, 2, "Жарма 0.5л", 30.0),
            (5, 2, 3, 4, 4, "Forester Energy 0.5л", 55.0),
            (6, 3, 4, 5, 5, "Абдыш-Ата сок яблоко 1л", 60.0),
        ])

        await db.commit()
        print("✅ Данные добавлены!")

asyncio.run(seed())
