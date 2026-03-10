from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import aiosqlite

router = Router()
DB_PATH = "bot.db"

# Все шаги анкеты
class StoreForm(StatesGroup):
    contact_name = State()
    phone = State()
    phone2 = State()
    store_name = State()
    city = State()
    address = State()
    store_type = State()
    delivery_time = State()
    payment_type = State()
    delivery_comment = State()

# Кнопки выбора роли
def role_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏪 Магазин")],
            [KeyboardButton(text="🏭 Дистрибьютор")]
        ],
        resize_keyboard=True
    )

# Главное меню магазина
def store_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Заказать")],
            [KeyboardButton(text="👤 Мои данные"), KeyboardButton(text="📦 Мои заказы")],
            [KeyboardButton(text="💬 Поддержка")]
        ],
        resize_keyboard=True
    )

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Добро пожаловать!\n\n"
        "Это система оформления заказов.\n"
        "Пожалуйста, выберите вашу роль:",
        reply_markup=role_keyboard()
    )

@router.message(F.text == "🏪 Магазин")
async def role_store(message: Message, state: FSMContext):
    # Проверяем есть ли уже анкета
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id FROM stores WHERE user_id = ?",
            (message.from_user.id,)
        )
        store = await cursor.fetchone()

    if store:
        await message.answer(
            "✅ Вы уже зарегистрированы!\n\nЧто хотите сделать?",
            reply_markup=store_menu()
        )
    else:
        await message.answer(
            "📝 Заполним анкету магазина.\n"
            "Это нужно сделать один раз.\n\n"
            "Введите ФИО контактного лица:",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(StoreForm.contact_name)

# --- Шаги анкеты ---

@router.message(StoreForm.contact_name)
async def get_contact_name(message: Message, state: FSMContext):
    await state.update_data(contact_name=message.text)
    await message.answer("📱 Введите номер телефона:")
    await state.set_state(StoreForm.phone)

@router.message(StoreForm.phone)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer(
        "📱 Введите дополнительный номер телефона:\n"
        "(или нажмите /skip чтобы пропустить)"
    )
    await state.set_state(StoreForm.phone2)

@router.message(StoreForm.phone2)
async def get_phone2(message: Message, state: FSMContext):
    if message.text == "/skip":
        await state.update_data(phone2="")
    else:
        await state.update_data(phone2=message.text)
    await message.answer("🏪 Введите название магазина:")
    await state.set_state(StoreForm.store_name)

@router.message(StoreForm.store_name)
async def get_store_name(message: Message, state: FSMContext):
    await state.update_data(store_name=message.text)
    await message.answer("🏙 Введите город / район:")
    await state.set_state(StoreForm.city)

@router.message(StoreForm.city)
async def get_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("📍 Введите адрес доставки:")
    await state.set_state(StoreForm.address)

@router.message(StoreForm.address)
async def get_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏠 Магазин у дома"), KeyboardButton(text="🏪 Минимаркет")],
            [KeyboardButton(text="🏬 Супермаркет"), KeyboardButton(text="☕ Кафе/Бар/Ресторан")],
            [KeyboardButton(text="📦 Оптовая точка"), KeyboardButton(text="🔹 Другое")]
        ],
        resize_keyboard=True
    )
    await message.answer("🏷 Выберите тип торговой точки:", reply_markup=keyboard)
    await state.set_state(StoreForm.store_type)

@router.message(StoreForm.store_type)
async def get_store_type(message: Message, state: FSMContext):
    await state.update_data(store_type=message.text)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌅 Утро"), KeyboardButton(text="☀️ День")],
            [KeyboardButton(text="🌆 Вечер"), KeyboardButton(text="🕐 В любое время")]
        ],
        resize_keyboard=True
    )
    await message.answer("🕐 Удобное время доставки:", reply_markup=keyboard)
    await state.set_state(StoreForm.delivery_time)

@router.message(StoreForm.delivery_time)
async def get_delivery_time(message: Message, state: FSMContext):
    await state.update_data(delivery_time=message.text)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💵 Наличные"), KeyboardButton(text="💳 Перевод")],
            [KeyboardButton(text="🏦 Безнал"), KeyboardButton(text="❓ Уточняется")]
        ],
        resize_keyboard=True
    )
    await message.answer("💰 Форма оплаты при получении:", reply_markup=keyboard)
    await state.set_state(StoreForm.payment_type)

@router.message(StoreForm.payment_type)
async def get_payment_type(message: Message, state: FSMContext):
    await state.update_data(payment_type=message.text)
    await message.answer(
        "💬 Комментарий к доставке:\n"
        "(например: вход со двора, звонить заранее)\n\n"
        "Или нажмите /skip",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(StoreForm.delivery_comment)

@router.message(StoreForm.delivery_comment)
async def get_delivery_comment(message: Message, state: FSMContext):
    if message.text == "/skip":
        await state.update_data(delivery_comment="")
    else:
        await state.update_data(delivery_comment=message.text)

    data = await state.get_data()

    # Сохраняем в БД
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO stores 
            (user_id, contact_name, phone, phone2, store_name, city, address, 
             store_type, delivery_time, payment_type, delivery_comment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            message.from_user.id,
            data["contact_name"],
            data["phone"],
            data.get("phone2", ""),
            data["store_name"],
            data["city"],
            data["address"],
            data["store_type"],
            data["delivery_time"],
            data["payment_type"],
            data.get("delivery_comment", "")
        ))
        await db.commit()

    await state.clear()
    await message.answer(
        f"✅ Анкета заполнена!\n\n"
        f"👤 {data['contact_name']}\n"
        f"📱 {data['phone']}\n"
        f"🏪 {data['store_name']}\n"
        f"📍 {data['address']}, {data['city']}\n\n"
        f"Теперь можете оформлять заказы!",
        reply_markup=store_menu()
    )

@router.message(F.text == "🏭 Дистрибьютор")
async def role_distributor(message: Message):
    await message.answer("Раздел дистрибьютора в разработке 🔧")

@router.message(F.text == "📦 Мои заказы")
async def my_orders(message: Message):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id FROM stores WHERE user_id = ?",
            (message.from_user.id,)
        )
        store = await cursor.fetchone()

        if not store:
            await message.answer("❗ Сначала заполните анкету. Нажмите /start")
            return

        cursor = await db.execute(
            """SELECT id, distributor, product, quantity, total_price, status, created_at 
               FROM orders WHERE store_id = ? 
               ORDER BY created_at DESC LIMIT 10""",
            (store[0],)
        )
        orders = await cursor.fetchall()

    if not orders:
        await message.answer("📭 У вас пока нет заказов.")
        return

    text = "📦 *Ваши последние заказы:*\n\n"
    for o in orders:
        order_id, distributor, product, qty, total, status, created_at = o
        status_emoji = {
            "new": "🆕",
            "sent": "📤",
            "done": "✅",
            "cancelled": "❌"
        }.get(status, "🔹")

        text += (
            f"{status_emoji} *Заказ #{order_id}*\n"
            f"🏭 {distributor}\n"
            f"🛍 {product} — {qty} шт.\n"
            f"💰 {total} сом\n"
            f"🕐 {created_at[:16]}\n"
            f"{'—'*20}\n"
        )

    await message.answer(text, parse_mode="Markdown")


@router.message(F.text == "👤 Мои данные")
async def my_profile(message: Message):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """SELECT contact_name, phone, phone2, store_name, 
               address, city, store_type, delivery_time, payment_type, delivery_comment
               FROM stores WHERE user_id = ?""",
            (message.from_user.id,)
        )
        store = await cursor.fetchone()

    if not store:
        await message.answer("❗ Анкета не заполнена. Нажмите /start")
        return

    contact_name, phone, phone2, store_name, address, city, \
    store_type, delivery_time, payment_type, delivery_comment = store

    text = (
        f"👤 *Ваши данные:*\n\n"
        f"👤 ФИО: {contact_name}\n"
        f"📱 Телефон: {phone}\n"
        f"📱 Доп. телефон: {phone2 or '—'}\n"
        f"🏪 Магазин: {store_name}\n"
        f"📍 Адрес: {address}\n"
        f"🏙 Город: {city}\n"
        f"🏷 Тип точки: {store_type}\n"
        f"🕐 Время доставки: {delivery_time}\n"
        f"💰 Оплата: {payment_type}\n"
        f"💬 Комментарий: {delivery_comment or '—'}\n"
    )

    edit_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✏️ Редактировать данные")],
            [KeyboardButton(text="🔙 Главное меню")]
        ],
        resize_keyboard=True
    )

    await message.answer(text, parse_mode="Markdown", reply_markup=edit_keyboard)


@router.message(F.text == "🔙 Главное меню")
async def back_to_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Главное меню:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🛒 Заказать")],
                [KeyboardButton(text="👤 Мои данные"), KeyboardButton(text="📦 Мои заказы")],
                [KeyboardButton(text="💬 Поддержка")]
            ],
            resize_keyboard=True
        )
    )

@router.message(F.text == "✏️ Редактировать данные")
async def edit_profile(message: Message, state: FSMContext):
    await message.answer(
        "📝 Заполним анкету заново.\n\nВведите ФИО контактного лица:",
        reply_markup=ReplyKeyboardRemove()
    )
    # Удаляем старую анкету
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM stores WHERE user_id = ?",
            (message.from_user.id,)
        )
        await db.commit()
    await state.set_state(StoreForm.contact_name)


@router.message(F.text == "💬 Поддержка")
async def support(message: Message):
    await message.answer(
        "💬 *Поддержка*\n\n"
        "По всем вопросам обращайтесь:\n"
        "👤 @admin_username\n"
        "📱 +996 XXX XXX XXX",
        parse_mode="Markdown"
    )
