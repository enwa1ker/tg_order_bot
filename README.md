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
```bash
git clone https://github.com/enwa1ker/tg_order_bot.git
cd tg_order_bot
```

### 2. Создай виртуальное окружение
```bash
python -m venv venv
```

Windows:
```bash
venv\Scripts\activate
```

Mac/Linux:
```bash
source venv/bin/activate
```

### 3. Установи зависимости
```bash
pip install aiogram aiosqlite python-dotenv gspread google-auth
```

### 4. Создай файл .env в корне проекта
```
BOT_TOKEN=токен_от_BotFather
ADMIN_ID=твой_telegram_id
SPREADSHEET_ID=id_google_таблицы
```

### 5. Добавь credentials.json
- Зайди на [console.cloud.google.com](https://console.cloud.google.com)
- Создай Service Account
- Скачай JSON ключ → переименуй в `credentials.json`
- Положи в корень проекта
- Дай доступ к Google таблице (email из credentials.json)

### 6. Создай таблицы в БД
```bash
python init_db.py
```

### 7. Заполни тестовые данные
```bash
python database/seed.py
```

### 8. Запусти бота
```bash
python bot.py
```

## Структура проекта
```
tg_order_bot/
├── bot.py                  # Точка входа и инициализация роутеров
├── config.py               # Загрузка env и констант
├── init_db.py              # Скрипт миграции базы данных
├── database/
│   ├── models.py           # Схемы таблиц БД
│   └── seed.py             # Скрипт первичного наполнения
├── handlers/
│   ├── start.py            # Обработка /start, анкеты и профиля
│   └── order.py            # Логика выбора товаров и оформления заказа
├── utils/
│   ├── notify.py           # Сервис отправки уведомлений
│   └── sheets.py           # Взаимодействие с Google Sheets API
└── keyboards/
    └── reply.py            # Сборка статических и динамических кнопок
```

## Важно
- `.env` — не заливать в git (токен бота)
- `credentials.json` — не заливать в git (доступ к Google)
- `bot.db` — не заливать в git (база данных)

## Следующие этапы
- [ ] Корзина (несколько товаров)
- [ ] Статусы заказов
- [ ] Назначение менеджеров
- [ ] Веб-админ панель
- [ ] Деплой на сервер
