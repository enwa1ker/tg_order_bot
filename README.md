# TG Order Bot 🤖

Telegram-бот для приёма и маршрутизации заказов от магазинов к дистрибьюторам.

## Что умеет бот
- Анкета магазина (заполняется один раз)
- Выбор дистрибьютора → категория → подкатегория → бренд → товар
- Оформление заказа + расчёт суммы
- Уведомления админу и менеджеру дистрибьютора
- Запись заказов в Google Sheets
- История заказов / просмотр данных

## Технологии
- Python 3.11
- aiogram 3
- SQLite
- Google Sheets API

## Установка

### 1. Клонируй репозиторий
git clone https://github.com/enwa1ker/tg_order_bot.git
cd tg_order_bot

### 2. Создай виртуальное окружение
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

### 3. Установи зависимости
pip install aiogram aiosqlite python-dotenv gspread google-auth

### 4. Создай файл .env в корне проекта
BOT_TOKEN=токен_от_BotFather
ADMIN_ID=твой_telegram_id
SPREADSHEET_ID=id_google_таблицы

### 5. Добавь credentials.json
- Зайди на console.cloud.google.com
- Создай Service Account
- Скачай JSON ключ
- Переименуй в credentials.json
- Положи в корень проекта
- Дай доступ к Google таблице (email из credentials.json)

### 6. Создай таблицы в БД
python init_db.py

### 7. Заполни тестовые данные
python database/seed.py

### 8. Запусти бота
python bot.py

## Структура проекта
tg_order_bot/
├── bot.py                  # точка входа
├── config.py               # конфиг
├── init_db.py              # создание таблиц
├── database/
│   ├── models.py           # таблицы БД
│   └── seed.py             # тестовые данные
├── handlers/
│   ├── start.py            # старт, анкета, профиль
│   └── order.py            # оформление заказа
├── utils/
│   ├── notify.py           # уведомления
│   └── sheets.py           # Google Sheets
└── keyboards/
    └── reply.py            # клавиатуры

## Важно
- .env — не заливать в git (токен бота)
- credentials.json — не заливать в git (доступ к Google)
- bot.db — не заливать в git (база данных)

## Следующие этапы
- [ ] Корзина (несколько товаров)
- [ ] Статусы заказов
- [ ] Назначение менеджеров
- [ ] Веб-админ панель
- [ ] Деплой на сервер
```

Сохрани и запушь:
```
git add README.md
git commit -m "add README"
git push origin master
