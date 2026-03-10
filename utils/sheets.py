import gspread
from google.oauth2.service_account import Credentials
from config import SPREADSHEET_ID
from datetime import datetime

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_sheet():
    creds = Credentials.from_service_account_file(
        "credentials.json", scopes=SCOPES
    )
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID)

def init_sheets():
    sheet = get_sheet()

    # Создаём листы если их нет
    existing = [s.title for s in sheet.worksheets()]

    if "Orders" not in existing:
        ws = sheet.add_worksheet("Orders", rows=1000, cols=20)
        ws.append_row([
            "ID", "Дата", "Магазин", "Контакт", "Телефон",
            "Адрес", "Город", "Компания", "Товар",
            "Количество", "Цена", "Сумма", "Статус"
        ])

    if "Clients" not in existing:
        ws = sheet.add_worksheet("Clients", rows=1000, cols=15)
        ws.append_row([
            "ID", "TG ID", "ФИО", "Телефон", "Магазин",
            "Адрес", "Город", "Тип", "Дата регистрации"
        ])

async def save_order_to_sheets(order_data: dict, store_data: dict):
    try:
        sheet = get_sheet()
        ws = sheet.worksheet("Orders")

        ws.append_row([
            order_data.get("order_id", ""),
            datetime.now().strftime("%d.%m.%Y %H:%M"),
            store_data["store_name"],
            store_data["contact_name"],
            store_data["phone"],
            store_data["address"],
            store_data["city"],
            order_data["distributor_name"],
            order_data["product_name"],
            order_data["quantity"],
            order_data["unit_price"],
            order_data["total"],
            "Новый"
        ])
        return True
    except Exception as e:
        print(f"Ошибка записи в Sheets: {e}")
        return False

async def save_client_to_sheets(store_data: dict):
    try:
        sheet = get_sheet()
        ws = sheet.worksheet("Clients")

        # Проверяем нет ли уже такого клиента
        all_values = ws.col_values(2)  # TG ID колонка
        if str(store_data["user_id"]) in all_values:
            return True

        ws.append_row([
            "",
            store_data["user_id"],
            store_data["contact_name"],
            store_data["phone"],
            store_data["store_name"],
            store_data["address"],
            store_data["city"],
            store_data.get("store_type", ""),
            datetime.now().strftime("%d.%m.%Y")
        ])
        return True
    except Exception as e:
        print(f"Ошибка записи клиента в Sheets: {e}")
        return False