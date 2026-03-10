from aiogram import Bot
from config import ADMIN_ID
import aiosqlite

DB_PATH = "bot.db"

async def notify_admin(bot: Bot, order_data: dict, store_data: dict):
    text = (
        f"🆕 *НОВЫЙ ЗАКАЗ*\n\n"
        f"👤 Клиент: {store_data['contact_name']}\n"
        f"🏪 Магазин: {store_data['store_name']}\n"
        f"📱 Телефон: {store_data['phone']}\n"
        f"📍 Адрес: {store_data['address']}, {store_data['city']}\n\n"
        f"🏭 Компания: {order_data['distributor_name']}\n"
        f"🛍 Товар: {order_data['product_name']}\n"
        f"📦 Количество: {order_data['quantity']} шт.\n"
        f"💰 Сумма: *{order_data['total']} сом*\n\n"
        f"🕐 Время: {order_data['created_at']}\n"
        f"🆔 TG ID: {store_data['user_id']}"
    )
    await bot.send_message(ADMIN_ID, text, parse_mode="Markdown")

    # Уведомляем дополнительных админов из БД
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT telegram_id FROM admins WHERE is_active = 1"
        )
        admins = await cursor.fetchall()
        for admin in admins:
            try:
                await bot.send_message(admin[0], text, parse_mode="Markdown")
            except Exception:
                pass

async def notify_manager(bot: Bot, distributor_id: int, order_data: dict, store_data: dict):
    text = (
        f"📋 *ЗАКАЗ ДЛЯ ВАШЕЙ КОМПАНИИ*\n\n"
        f"🏪 Магазин: {store_data['store_name']}\n"
        f"📱 Телефон: {store_data['phone']}\n"
        f"📍 Адрес доставки: {store_data['address']}, {store_data['city']}\n\n"
        f"🛍 Товар: {order_data['product_name']}\n"
        f"📦 Количество: {order_data['quantity']} шт.\n"
        f"💰 Сумма: *{order_data['total']} сом*\n\n"
        f"💬 Комментарий: {store_data.get('delivery_comment', '—')}\n"
        f"🕐 Время заказа: {order_data['created_at']}"
    )

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """SELECT telegram_chat_id FROM distributor_managers 
               WHERE distributor_id = ? AND is_active = 1""",
            (distributor_id,)
        )
        managers = await cursor.fetchall()

    if not managers:
        # Нет менеджера — пишем админу
        await bot.send_message(
            ADMIN_ID,
            f"⚠️ У компании нет менеджера! Заказ:\n\n{text}",
            parse_mode="Markdown"
        )
        return

    for manager in managers:
        try:
            await bot.send_message(manager[0], text, parse_mode="Markdown")
        except Exception:
            await bot.send_message(
                ADMIN_ID,
                f"⚠️ Не удалось отправить уведомление менеджеру {manager[0]}",
                parse_mode="Markdown"
            )