import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import BOT_TOKEN, PROVIDER_TOKEN, STARS_PACKAGES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ─── /start ───────────────────────────────────────────────────────────────────

@dp.message(CommandStart())
async def cmd_start(message: Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="⭐ Купить звёзды", callback_data="buy_stars")
    builder.button(text="ℹ️ Как это работает", callback_data="how_it_works")
    builder.adjust(1)

    await message.answer(
        "👋 <b>Добро пожаловать!</b>\n\n"
        "Здесь ты можешь купить <b>Telegram Stars ⭐</b> за <b>TON 💎</b>.\n\n"
        "Stars используются для:\n"
        "• Поддержки авторов и ботов\n"
        "• Покупки цифровых товаров\n"
        "• Отправки реакций\n\n"
        "Нажми кнопку ниже, чтобы выбрать пакет 👇",
        parse_mode="HTML",
        reply_markup=builder.as_markup()
    )


# ─── Как работает ─────────────────────────────────────────────────────────────

@dp.callback_query(F.data == "how_it_works")
async def how_it_works(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="⭐ Купить звёзды", callback_data="buy_stars")
    builder.button(text="◀️ Назад", callback_data="back_start")
    builder.adjust(1)

    await callback.message.edit_text(
        "ℹ️ <b>Как это работает?</b>\n\n"
        "1️⃣ Выбери нужный пакет звёзд\n"
        "2️⃣ Оплати через Telegram Payments (TON)\n"
        "3️⃣ Звёзды автоматически зачислятся на твой аккаунт\n\n"
        "💎 <b>Оплата</b> — через встроенную систему Telegram Payments.\n"
        "Твои данные защищены платформой Telegram.\n\n"
        "⚡ Зачисление — мгновенное после оплаты.",
        parse_mode="HTML",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


# ─── Список пакетов ───────────────────────────────────────────────────────────

@dp.callback_query(F.data.in_({"buy_stars", "back_packages"}))
async def show_packages(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    for pkg in STARS_PACKAGES:
        label = f"⭐ {pkg['stars']} звёзд — {pkg['ton']} TON"
        builder.button(text=label, callback_data=f"buy_{pkg['id']}")
    builder.button(text="◀️ Назад", callback_data="back_start")
    builder.adjust(1)

    await callback.message.edit_text(
        "⭐ <b>Выбери пакет звёзд</b>\n\n"
        "Все пакеты зачисляются мгновенно после оплаты 💳\n\n"
        + "\n".join(
            f"• <b>{p['stars']} Stars</b> = {p['ton']} TON (~{p['usd']}$)"
            for p in STARS_PACKAGES
        ),
        parse_mode="HTML",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@dp.callback_query(F.data == "back_start")
async def back_to_start(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="⭐ Купить звёзды", callback_data="buy_stars")
    builder.button(text="ℹ️ Как это работает", callback_data="how_it_works")
    builder.adjust(1)

    await callback.message.edit_text(
        "👋 <b>Добро пожаловать!</b>\n\n"
        "Здесь ты можешь купить <b>Telegram Stars ⭐</b> за <b>TON 💎</b>.\n\n"
        "Stars используются для:\n"
        "• Поддержки авторов и ботов\n"
        "• Покупки цифровых товаров\n"
        "• Отправки реакций\n\n"
        "Нажми кнопку ниже, чтобы выбрать пакет 👇",
        parse_mode="HTML",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


# ─── Выбор пакета → инвойс ────────────────────────────────────────────────────

@dp.callback_query(F.data.startswith("buy_"))
async def send_invoice(callback: CallbackQuery):
    pkg_id = callback.data.replace("buy_", "")
    pkg = next((p for p in STARS_PACKAGES if p["id"] == pkg_id), None)

    if not pkg:
        await callback.answer("❌ Пакет не найден", show_alert=True)
        return

    # amount в наноTON (1 TON = 1_000_000_000 нано)
    amount_nanoton = int(pkg["ton"] * 1_000_000_000)

    prices = [LabeledPrice(label=f"⭐ {pkg['stars']} Telegram Stars", amount=amount_nanoton)]

    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=f"⭐ {pkg['stars']} Telegram Stars",
        description=(
            f"Покупка {pkg['stars']} звёзд Telegram за {pkg['ton']} TON.\n"
            "Зачисление мгновенное после подтверждения оплаты."
        ),
        payload=f"stars_{pkg['id']}_{callback.from_user.id}",
        provider_token=PROVIDER_TOKEN,   # "" для XTR / TON Stars payments
        currency="XTR",                  # XTR = Telegram Stars currency / или TON
        prices=prices,
        start_parameter=f"buy_{pkg['id']}",
        photo_url="https://telegram.org/img/t_logo.png",
        photo_width=100,
        photo_height=100,
        need_name=False,
        need_email=False,
        need_phone_number=False,
        is_flexible=False,
    )
    await callback.answer()


# ─── Pre-checkout (обязательно отвечать ОК) ───────────────────────────────────

@dp.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    # Здесь можно проверить наличие товара, лимиты и т.д.
    await pre_checkout_query.answer(ok=True)


# ─── Успешная оплата ──────────────────────────────────────────────────────────

@dp.message(F.successful_payment)
async def successful_payment(message: Message):
    payment = message.successful_payment
    payload = payment.invoice_payload  # "stars_{id}_{user_id}"

    parts = payload.split("_")
    pkg_id = parts[1] if len(parts) >= 2 else "?"
    pkg = next((p for p in STARS_PACKAGES if p["id"] == pkg_id), None)
    stars = pkg["stars"] if pkg else "?"

    logger.info(
        f"✅ Успешная оплата от {message.from_user.id} | "
        f"payload={payload} | charge_id={payment.telegram_payment_charge_id}"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="⭐ Купить ещё", callback_data="buy_stars")
    builder.adjust(1)

    await message.answer(
        f"✅ <b>Оплата прошла успешно!</b>\n\n"
        f"⭐ <b>{stars} Stars</b> зачислены на твой аккаунт.\n\n"
        f"🧾 ID транзакции:\n<code>{payment.telegram_payment_charge_id}</code>\n\n"
        f"Спасибо за покупку! 🎉",
        parse_mode="HTML",
        reply_markup=builder.as_markup()
    )


# ─── /help ────────────────────────────────────────────────────────────────────

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "🆘 <b>Помощь</b>\n\n"
        "/start — главное меню\n"
        "/help — эта справка\n\n"
        "По вопросам обращайся к администратору бота.",
        parse_mode="HTML"
    )


# ─── Запуск ───────────────────────────────────────────────────────────────────

async def main():
    logger.info("🤖 Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
