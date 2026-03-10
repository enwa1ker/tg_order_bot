from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

router = Router()

# Кнопки выбора роли
def role_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏪 Магазин")],
            [KeyboardButton(text="🏭 Дистрибьютор")]
        ],
        resize_keyboard=True
    )

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 Добро пожаловать!\n\n"
        "Это система оформления заказов.\n"
        "Пожалуйста, выберите вашу роль:",
        reply_markup=role_keyboard()
    )

@router.message(F.text == "🏪 Магазин")
async def role_store(message: Message):
    await message.answer("Вы выбрали: Магазин\n\nСейчас заполним анкету...")

@router.message(F.text == "🏭 Дистрибьютор")
async def role_distributor(message: Message):
    await message.answer("Раздел дистрибьютора в разработке 🔧")
