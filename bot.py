import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from keyboards import (
    main_menu_kb,
    recipient_kb,
    stars_amount_kb,
    payment_method_kb,
    confirm_kb,
    cancel_kb,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


class BuyStarsFlow(StatesGroup):
    waiting_for_recipient = State()
    waiting_for_amount = State()
    waiting_for_custom_amount = State()
    waiting_for_payment = State()
    confirming = State()


STAR_PRICES = {
    50: 59,
    100: 119,
    150: 178,
    250: 297,
    350: 416,
    500: 595,
    750: 892,
    1000: 1190,
    1500: 1785,
    2500: 2975,
    5000: 5950,
    10000: 11900,
}

PAYMENT_METHODS = {
    "sbp_1": ("СБП [1]", 6.0),
    "sbp": ("СБП", 8.0),
    "card": ("Карта", 8.0),
    "cryptobot": ("CryptoBot", 3.0),
    "ton": ("TON", 0.0),
    "lolzteam": ("LolzTeam", 4.0),
    "usdt": ("USDT (TON)", 0.0),
}


# ─── /start ────────────────────────────────────────────────────────────────────

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer_photo(
        photo="https://i.imgur.com/placeholder_main.jpg",  # замените на свой баннер
        caption=(
            "✨ *Добро пожаловать!*\n\n"
            "🎁 Покупайте Звёзды, Premium и пополняйте баланс за пару кликов.\n\n"
            "📦 Выдача товаров моментальна!"
        ),
        parse_mode="Markdown",
        reply_markup=main_menu_kb(),
    )


# ─── Главное меню ──────────────────────────────────────────────────────────────

@dp.callback_query(F.data == "buy_stars")
async def buy_stars_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BuyStarsFlow.waiting_for_recipient)
    await callback.message.edit_caption(
        caption=(
            "✈️ Введите юзернейм кому отправить звёзды\n"
            "*(пример: @username)*:"
        ),
        parse_mode="Markdown",
        reply_markup=recipient_kb(),
    )
    await callback.answer()


@dp.callback_query(F.data == "buy_premium")
async def buy_premium(callback: CallbackQuery):
    await callback.answer("🔜 Раздел Premium скоро будет доступен!", show_alert=True)


@dp.callback_query(F.data == "buy_ton")
async def buy_ton(callback: CallbackQuery):
    await callback.answer("🔜 Раздел TON скоро будет доступен!", show_alert=True)


@dp.callback_query(F.data == "buy_gift")
async def buy_gift(callback: CallbackQuery):
    await callback.answer("🔜 Раздел подарков скоро будет доступен!", show_alert=True)


@dp.callback_query(F.data == "weekly_raffle")
async def weekly_raffle(callback: CallbackQuery):
    await callback.answer("🎰 Еженедельный розыгрыш скоро!", show_alert=True)


@dp.callback_query(F.data == "create_check")
async def create_check(callback: CallbackQuery):
    await callback.answer("🧾 Функция чека скоро будет доступна!", show_alert=True)


@dp.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery):
    user = callback.from_user
    await callback.message.edit_caption(
        caption=(
            f"👤 *Профиль*\n\n"
            f"🆔 ID: `{user.id}`\n"
            f"👤 Имя: {user.full_name}\n"
            f"📛 Username: @{user.username or '—'}"
        ),
        parse_mode="Markdown",
        reply_markup=cancel_kb("main_menu"),
    )
    await callback.answer()


@dp.callback_query(F.data == "support")
async def support(callback: CallbackQuery):
    await callback.answer("💬 Поддержка: @support (замените на реальный контакт)", show_alert=True)


@dp.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_caption(
        caption=(
            "✨ *Добро пожаловать!*\n\n"
            "🎁 Покупайте Звёзды, Premium и пополняйте баланс за пару кликов.\n\n"
            "📦 Выдача товаров моментальна!"
        ),
        parse_mode="Markdown",
        reply_markup=main_menu_kb(),
    )
    await callback.answer()


# ─── Получатель ────────────────────────────────────────────────────────────────

@dp.callback_query(F.data == "recipient_self", BuyStarsFlow.waiting_for_recipient)
async def recipient_self(callback: CallbackQuery, state: FSMContext):
    username = f"@{callback.from_user.username}" if callback.from_user.username else f"ID:{callback.from_user.id}"
    await state.update_data(recipient=username)
    await _show_star_amounts(callback, state, username)


@dp.message(BuyStarsFlow.waiting_for_recipient)
async def recipient_entered(message: Message, state: FSMContext):
    username = message.text.strip()
    if not username.startswith("@"):
        username = "@" + username
    await state.update_data(recipient=username)

    # отправляем новое сообщение с выбором количества
    sent = await message.answer_photo(
        photo="https://i.imgur.com/placeholder_stars.jpg",
        caption=_stars_caption(username),
        parse_mode="Markdown",
        reply_markup=stars_amount_kb(),
    )
    await state.update_data(bot_msg_id=sent.message_id)
    await state.set_state(BuyStarsFlow.waiting_for_amount)


async def _show_star_amounts(callback: CallbackQuery, state: FSMContext, username: str):
    await state.set_state(BuyStarsFlow.waiting_for_amount)
    await callback.message.edit_caption(
        caption=_stars_caption(username),
        parse_mode="Markdown",
        reply_markup=stars_amount_kb(),
    )
    await callback.answer()


def _stars_caption(username: str) -> str:
    return (
        f"👤 Получатель: *{username}*\n\n"
        "🌟 Выберите кол-во звёзд для покупки или укажите своё:"
    )


# ─── Количество звёзд ──────────────────────────────────────────────────────────

@dp.callback_query(F.data.startswith("stars_"), BuyStarsFlow.waiting_for_amount)
async def stars_selected(callback: CallbackQuery, state: FSMContext):
    amount = int(callback.data.replace("stars_", ""))
    data = await state.get_data()
    recipient = data["recipient"]
    price = STAR_PRICES[amount]

    await state.update_data(amount=amount, price=price)
    await state.set_state(BuyStarsFlow.waiting_for_payment)

    await callback.message.edit_caption(
        caption=(
            f"Вы покупаете *{amount}* ⭐ для *{recipient}*\n\n"
            "💳 Выберите счёт для оплаты:"
        ),
        parse_mode="Markdown",
        reply_markup=payment_method_kb(),
    )
    await callback.answer()


@dp.callback_query(F.data == "custom_amount", BuyStarsFlow.waiting_for_amount)
async def custom_amount(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BuyStarsFlow.waiting_for_custom_amount)
    await callback.message.edit_caption(
        caption="✏️ Введите нужное количество звёзд (минимум 50):",
        reply_markup=cancel_kb("main_menu"),
    )
    await callback.answer()


@dp.message(BuyStarsFlow.waiting_for_custom_amount)
async def custom_amount_entered(message: Message, state: FSMContext):
    try:
        amount = int(message.text.strip())
        if amount < 50:
            await message.answer("❌ Минимум 50 звёзд. Введите другое число:")
            return
    except ValueError:
        await message.answer("❌ Введите корректное число:")
        return

    # считаем цену (~1.19 руб за звезду)
    price = round(amount * 1.19)
    data = await state.get_data()
    recipient = data["recipient"]

    await state.update_data(amount=amount, price=price)
    await state.set_state(BuyStarsFlow.waiting_for_payment)

    await message.answer_photo(
        photo="https://i.imgur.com/placeholder_stars.jpg",
        caption=(
            f"Вы покупаете *{amount}* ⭐ для *{recipient}*\n\n"
            "💳 Выберите счёт для оплаты:"
        ),
        parse_mode="Markdown",
        reply_markup=payment_method_kb(),
    )


# ─── Способ оплаты ─────────────────────────────────────────────────────────────

@dp.callback_query(F.data.startswith("pay_"), BuyStarsFlow.waiting_for_payment)
async def payment_selected(callback: CallbackQuery, state: FSMContext):
    method_key = callback.data.replace("pay_", "")
    method_name, fee_pct = PAYMENT_METHODS[method_key]
    data = await state.get_data()

    amount = data["amount"]
    base_price = data["price"]
    recipient = data["recipient"]
    final_price = round(base_price * (1 + fee_pct / 100), 2)

    await state.update_data(method=method_name, final_price=final_price)
    await state.set_state(BuyStarsFlow.confirming)

    await callback.message.edit_caption(
        caption=(
            f"🔒 *Счёт {method_name}*\n\n"
            f"👤 Получатель: *{recipient}*\n"
            f"🎁 Товар: *{amount}* ⭐\n"
            f"💰 Сумма: *{final_price}₽*\n\n"
            "❗ После успешной оплаты бот автоматически обработает ваш заказ"
        ),
        parse_mode="Markdown",
        reply_markup=confirm_kb(),
    )
    await callback.answer()


@dp.callback_query(F.data == "confirm_pay", BuyStarsFlow.confirming)
async def confirm_payment(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    # TODO: здесь интеграция с реальным платёжным шлюзом
    await callback.answer("✅ Заказ принят! (тестовый режим)", show_alert=True)
    await state.clear()

    await callback.message.edit_caption(
        caption=(
            "✅ *Заказ успешно создан!*\n\n"
            f"⭐ {data['amount']} звёзд для {data['recipient']}\n"
            f"💳 Способ оплаты: {data['method']}\n"
            f"💰 Сумма: {data['final_price']}₽\n\n"
            "📦 Выдача будет произведена автоматически после оплаты."
        ),
        parse_mode="Markdown",
        reply_markup=cancel_kb("main_menu"),
    )


# ─── Отмена ────────────────────────────────────────────────────────────────────

@dp.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_caption(
        caption=(
            "✨ *Добро пожаловать!*\n\n"
            "🎁 Покупайте Звёзды, Premium и пополняйте баланс за пару кликов.\n\n"
            "📦 Выдача товаров моментальна!"
        ),
        parse_mode="Markdown",
        reply_markup=main_menu_kb(),
    )
    await callback.answer("❌ Отменено")


# ─── Запуск ────────────────────────────────────────────────────────────────────

async def main():
    logger.info("Бот запущен ✅")
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
