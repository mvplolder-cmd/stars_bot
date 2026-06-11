from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Купить звёзды", callback_data="buy_stars")],
        [
            InlineKeyboardButton(text="🎁 Premium", callback_data="buy_premium"),
            InlineKeyboardButton(text="💎 TON", callback_data="buy_ton"),
        ],
        [InlineKeyboardButton(text="🎁 Купить подарок", callback_data="buy_gift")],
        [InlineKeyboardButton(text="🎰 Еженедельный розыгрыш", callback_data="weekly_raffle")],
        [
            InlineKeyboardButton(text="🧾 Создать чек", callback_data="create_check"),
            InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
        ],
        [InlineKeyboardButton(text="💬 Поддержка", callback_data="support")],
    ])


def recipient_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Себе", callback_data="recipient_self")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")],
    ])


def stars_amount_kb() -> InlineKeyboardMarkup:
    amounts = [50, 100, 150, 250, 350, 500, 750, 1000, 1500, 2500, 5000, 10000]
    prices = {
        50: 59, 100: 119, 150: 178, 250: 297,
        350: 416, 500: 595, 750: 892, 1000: 1190,
        1500: 1785, 2500: 2975, 5000: 5950, 10000: 11900,
    }

    rows = []
    for i in range(0, len(amounts), 2):
        row = []
        for amt in amounts[i:i+2]:
            row.append(InlineKeyboardButton(
                text=f"⭐ {amt} ({prices[amt]}₽)",
                callback_data=f"stars_{amt}",
            ))
        rows.append(row)

    rows.append([InlineKeyboardButton(text="⚙️ Указать своё количество", callback_data="custom_amount")])
    rows.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def payment_method_kb() -> InlineKeyboardMarkup:
    methods = [
        ("🏦 СБП [1] • 6%", "pay_sbp_1"),
        ("🏦 СБП • 8%", "pay_sbp"),
        ("💳 Карта • 8%", "pay_card"),
        ("🤖 CryptoBot • 3.0%", "pay_cryptobot"),
        ("💎 TON • 0.0%", "pay_ton"),
        ("🐊 LolzTeam • 4.0%", "pay_lolzteam"),
        ("💵 USDT (TON) • 0.0%", "pay_usdt"),
    ]
    rows = [[InlineKeyboardButton(text=label, callback_data=data)] for label, data in methods]
    rows.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить", callback_data="confirm_pay")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")],
    ])


def cancel_kb(back_to: str = "cancel") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data=back_to)],
    ])
