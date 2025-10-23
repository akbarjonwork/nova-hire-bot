# utils.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta

def generate_calendar(year: int | None = None, month: int | None = None) -> InlineKeyboardMarkup:
    now = datetime.now()
    year = year or now.year
    month = month or now.month

    next_month = month + 1 if month < 12 else 1
    next_month_year = year if month < 12 else year + 1
    days_in_month = (datetime(next_month_year, next_month, 1) - timedelta(days=1)).day

    inline_keyboard = []

    header_text = f"{year}-{month:02d}"
    inline_keyboard.append([InlineKeyboardButton(text=header_text, callback_data="ignore")])

    weekdays = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    inline_keyboard.append([InlineKeyboardButton(text=d, callback_data="ignore") for d in weekdays])

    first_weekday = datetime(year, month, 1).weekday()
    row = []

    for _ in range(first_weekday):
        row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))

    for day in range(1, days_in_month + 1):
        row.append(InlineKeyboardButton(text=str(day), callback_data=f"date:{year}-{month:02d}-{day:02d}"))
        if len(row) == 7:
            inline_keyboard.append(row)
            row = []

    if row:
        inline_keyboard.append(row)

    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    nav_row = [
        InlineKeyboardButton(text="⬅️", callback_data=f"cal:{prev_year}:{prev_month}"),
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_calendar"),
        InlineKeyboardButton(text="➡️", callback_data=f"cal:{next_year}:{next_month}")
    ]
    inline_keyboard.append(nav_row)

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
