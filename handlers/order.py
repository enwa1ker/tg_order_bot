from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import aiosqlite

from utils.sheets import save_client_to_sheets, save_order_to_sheets

router = Router()
DB_PATH = "bot.db"

class OrderFlow(StatesGroup):
    choosing_distributor = State()
    choosing_category = State()
    choosing_subcategory = State()
    choosing_brand = State()
    choosing_product = State()
    entering_quantity = State()

def make_keyboard(items):
    keyboard = [[KeyboardButton(text=item)] for item in items]
    keyboard.append([KeyboardButton(text="🔙 Назад в меню")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

@router.message(F.text == "🛒 Заказать")
async def choose_distributor(message: Message, state: FSMContext):
    # Проверяем анкету
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id FROM stores WHERE user_id = ?",
            (message.from_user.id,)
        )
        store = await cursor.fetchone()

    if not store:
        await message.answer("❗ Сначала заполните анкету. Нажмите /start")
        return

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, name FROM distributors WHERE is_active = 1"
        )
        distributors = await cursor.fetchall()

    if not distributors:
        await message.answer("❗ Нет доступных компаний. Обратитесь к администратору.")
        return

    names = [d[1] for d in distributors]
    await state.set_state(OrderFlow.choosing_distributor)
    await message.answer("🏭 Выберите дистрибьютора:", reply_markup=make_keyboard(names))

@router.message(OrderFlow.choosing_distributor)
async def choose_category(message: Message, state: FSMContext):
    if message.text == "🔙 Назад в меню":
        await state.clear()
        await message.answer("Главное меню:", reply_markup=main_menu())
        return

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id FROM distributors WHERE name = ? AND is_active = 1",
            (message.text,)
        )
        distributor = await cursor.fetchone()

    if not distributor:
        await message.answer("❗ Компания не найдена, попробуйте ещё раз.")
        return

    await state.update_data(distributor_id=distributor[0], distributor_name=message.text)

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, name FROM categories WHERE distributor_id = ? AND is_active = 1",
            (distributor[0],)
        )
        categories = await cursor.fetchall()

    names = [c[1] for c in categories]
    await state.update_data(categories=categories)
    await state.set_state(OrderFlow.choosing_category)
    await message.answer("📦 Выберите категорию:", reply_markup=make_keyboard(names))

@router.message(OrderFlow.choosing_category)
async def choose_subcategory(message: Message, state: FSMContext):
    if message.text == "🔙 Назад в меню":
        await state.clear()
        await message.answer("Главное меню:", reply_markup=main_menu())
        return

    data = await state.get_data()
    categories = data.get("categories", [])
    category = next((c for c in categories if c[1] == message.text), None)

    if not category:
        await message.answer("❗ Категория не найдена, попробуйте ещё раз.")
        return

    await state.update_data(category_id=category[0], category_name=message.text)

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, name FROM subcategories WHERE category_id = ? AND is_active = 1",
            (category[0],)
        )
        subcategories = await cursor.fetchall()

    names = [s[1] for s in subcategories]
    await state.update_data(subcategories=subcategories)
    await state.set_state(OrderFlow.choosing_subcategory)
    await message.answer("📂 Выберите подкатегорию:", reply_markup=make_keyboard(names))

@router.message(OrderFlow.choosing_subcategory)
async def choose_brand(message: Message, state: FSMContext):
    if message.text == "🔙 Назад в меню":
        await state.clear()
        await message.answer("Главное меню:", reply_markup=main_menu())
        return

    data = await state.get_data()
    subcategories = data.get("subcategories", [])
    subcategory = next((s for s in subcategories if s[1] == message.text), None)

    if not subcategory:
        await message.answer("❗ Подкатегория не найдена, попробуйте ещё раз.")
        return

    await state.update_data(subcategory_id=subcategory[0], subcategory_name=message.text)

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, name FROM brands WHERE subcategory_id = ? AND is_active = 1",
            (subcategory[0],)
        )
        brands = await cursor.fetchall()

    names = [b[1] for b in brands]
    await state.update_data(brands=brands)
    await state.set_state(OrderFlow.choosing_brand)
    await message.answer("🏷 Выберите бренд:", reply_markup=make_keyboard(names))

@router.message(OrderFlow.choosing_brand)
async def choose_product(message: Message, state: FSMContext):
    if message.text == "🔙 Назад в меню":
        await state.clear()
        await message.answer("Главное меню:", reply_markup=main_menu())
        return

    data = await state.get_data()
    brands = data.get("brands", [])
    brand = next((b for b in brands if b[1] == message.text), None)

    if not brand:
        await message.answer("❗ Бренд не найден, попробуйте ещё раз.")
        return

    await state.update_data(brand_id=brand[0], brand_name=message.text)

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """SELECT id, name, unit_price, stock_status 
               FROM products 
               WHERE brand_id = ? AND is_active = 1""",
            (brand[0],)
        )
        products = await cursor.fetchall()

    names = [p[1] for p in products]
    await state.update_data(products=products)
    await state.set_state(OrderFlow.choosing_product)
    await message.answer("🛍 Выберите товар:", reply_markup=make_keyboard(names))

@router.message(OrderFlow.choosing_product)
async def show_product_card(message: Message, state: FSMContext):
    if message.text == "🔙 Назад в меню":
        await state.clear()
        await message.answer("Главное меню:", reply_markup=main_menu())
        return

    data = await state.get_data()
    products = data.get("products", [])
    product = next((p for p in products if p[1] == message.text), None)

    if not product:
        await message.answer("❗ Товар не найден, попробуйте ещё раз.")
        return

    product_id, name, price, stock = product
    await state.update_data(
        product_id=product_id,
        product_name=name,
        unit_price=price
    )

    status_text = "✅ В наличии" if stock == "in_stock" else "❌ Нет в наличии"

    card_text = (
        f"🛍 *{name}*\n\n"
        f"💰 Цена: *{price} сом*\n"
        f"📦 Минимальный заказ: 1 шт.\n"
        f"📊 Статус: {status_text}\n\n"
        f"Введите количество товара:"
    )

    order_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔙 Назад в меню")]
        ],
        resize_keyboard=True
    )

    await state.set_state(OrderFlow.entering_quantity)
    await message.answer(card_text, parse_mode="Markdown", reply_markup=order_keyboard)

@router.message(OrderFlow.entering_quantity)
async def confirm_order(message: Message, state: FSMContext, bot: Bot):
    if message.text == "🔙 Назад в меню":
        await state.clear()
        await message.answer("Главное меню:", reply_markup=main_menu())
        return

    if not message.text.isdigit() or int(message.text) <= 0:
        await message.answer("❗ Введите корректное число (например: 10)")
        return

    quantity = int(message.text)
    data = await state.get_data()
    unit_price = data["unit_price"]
    total = unit_price * quantity
    from datetime import datetime
    created_at = datetime.now().strftime("%d.%m.%Y %H:%M")

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, contact_name, phone, store_name, address, city, delivery_comment FROM stores WHERE user_id = ?",
            (message.from_user.id,)
        )
        store = await cursor.fetchone()

        cursor = await db.execute("""
            INSERT INTO orders 
            (store_id, distributor, product, quantity, unit_price, total_price, status)
            VALUES (?, ?, ?, ?, ?, ?, 'new')
        """, (
            store[0],
            data["distributor_name"],
            data["product_name"],
            quantity,
            unit_price,
            total
        ))
        await db.commit()
        order_id = cursor.lastrowid

    await state.clear()

    order_data = {
        "distributor_name": data["distributor_name"],
        "product_name": data["product_name"],
        "quantity": quantity,
        "total": total,
        "created_at": created_at
    }

    store_data = {
        "user_id": message.from_user.id,
        "contact_name": store[1],
        "phone": store[2],
        "store_name": store[3],
        "address": store[4],
        "city": store[5],
        "delivery_comment": store[6]
    }

    # Отправляем уведомления
    from utils.notify import notify_admin, notify_manager
    await notify_admin(bot, order_data, store_data)
    await notify_manager(bot, data["distributor_id"], order_data, store_data)

    from utils.sheets import save_order_to_sheets, save_client_to_sheets

    # Записываем в Google Sheets
    order_data["order_id"] = order_id
    order_data["unit_price"] = unit_price
    sheets_ok = await save_order_to_sheets(order_data, store_data)
    await save_client_to_sheets(store_data)

    if not sheets_ok:
        await bot.send_message(ADMIN_ID, "⚠️ Не удалось записать заказ в Google Sheets!")

    confirm_text = (
        f"✅ *Заказ оформлен!*\n\n"
        f"🏭 Компания: {data['distributor_name']}\n"
        f"🛍 Товар: {data['product_name']}\n"
        f"📦 Количество: {quantity} шт.\n"
        f"💰 Сумма: *{total} сом*\n\n"
        f"🚚 Доставка: ориентировочно завтра\n"
        f"💵 Оплата при получении напрямую поставщику"
    )

    await message.answer(confirm_text, parse_mode="Markdown", reply_markup=main_menu())

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Заказать")],
            [KeyboardButton(text="👤 Мои данные"), KeyboardButton(text="📦 Мои заказы")],
            [KeyboardButton(text="💬 Поддержка")]
        ],
        resize_keyboard=True
    )