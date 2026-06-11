import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Токен твоего бота (получи у @BotFather)
BOT_TOKEN = "8611742410:AAHcNxvVvoCe7uEfv3POaw60hT6y0JpEHwA"
# ID администратора, которому будут приходить уведомления о новых оплатах по номеру
# Обновленный ID супергруппы (из ошибки: -1003792567158)
ADMIN_ID = -1003792567158

# Реквизиты для оплаты
PAYMENT_PHONE = "+7 (901) 653-44-21"
PAYMENT_BANK = "Сбербанк (Лиза Ш.)"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Состояния для оформления заказа
class OrderState(StatesGroup):
    waiting_for_username = State()
    waiting_for_amount = State()
    waiting_for_payment_confirm = State()

# --- КЛАВИАТУРЫ ---

def main_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="⭐ Купить звезды", callback_data="buy_stars"))
    builder.row(
        types.InlineKeyboardButton(text="🎁 Premium", callback_data="premium"),
        types.InlineKeyboardButton(text="💎 TON", callback_data="ton")
    )
    builder.row(types.InlineKeyboardButton(text="👤 Профиль", callback_data="profile"))
    return builder.as_markup()

def amount_kb():
    builder = InlineKeyboardBuilder()
    amounts = [50, 100, 150, 250, 500, 1000]
    for amt in amounts:
        price = int(amt * 1.18)
        builder.button(text=f"⭐ {amt} ({price}₽)", callback_data=f"amt_{amt}_{price}")
    builder.adjust(2)
    builder.row(types.InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"))
    return builder.as_markup()

def payment_methods_kb():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="💚 Сбербанк / СБП (По номеру) • 0%", callback_data="pay_sber"))
    builder.row(types.InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"))
    return builder.as_markup()

def confirm_payment_kb():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="✅ Я оплатил(а)", callback_data="payment_done"))
    builder.row(types.InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"))
    return builder.as_markup()

# --- ХЕНДЛЕРЫ ---

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 **Добро пожаловать!**\n\n"
        "🚀 Покупайте Звезды, Premium и пополняйте баланс за пару кликов.\n"
        "🎁 Выдача товаров моментальна!",
        reply_markup=main_menu_kb(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "cancel")
async def cancel_action(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Действие отменено.", reply_markup=main_menu_kb())

@dp.callback_query(F.data == "buy_stars")
async def start_buy_stars(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "✈️ **Введите юзернейм**, кому отправить звезды (пример: @username):",
        parse_mode="Markdown"
    )
    await state.set_state(OrderState.waiting_for_username)

@dp.message(OrderState.waiting_for_username)
async def process_username(message: types.Message, state: FSMContext):
    username = message.text.strip()
    if not username.startswith("@"):
        username = "@" + username
    
    await state.update_data(target_user=username)
    await message.answer("🔍 Выберите кол-во звезд для покупки:", reply_markup=amount_kb())
    await state.set_state(OrderState.waiting_for_amount)

@dp.callback_query(OrderState.waiting_for_amount, F.data.startswith("amt_"))
async def process_amount(callback: types.CallbackQuery, state: FSMContext):
    _, amt, price = callback.data.split("_")
    await state.update_data(amount=amt, price=price)
    
    data = await state.get_data()
    await callback.message.edit_text(
        f"Вы покупаете **{amt} ⭐** для {data['target_user']}\n\n"
        f"💰 Выберите счет для оплаты:",
        reply_markup=payment_methods_kb(),
        parse_mode="Markdown"
    )

@dp.callback_query(OrderState.waiting_for_amount, F.data == "pay_sber")
async def process_sber_payment(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    text = (
        f"💳 **Счет на оплату по номеру**\n\n"
        f"👤 Получатель: {data['target_user']}\n"
        f"📦 Товар: {data['amount']} ⭐\n"
        f"💵 Сумма: **{data['price']} ₽**\n\n"
        f"--- РЕКВИЗИТЫ ДЛЯ ПЕРЕВОДА ---\n"
        f"📱 Номер: `{PAYMENT_PHONE}`\n"
        f"🏦 Банк: {PAYMENT_BANK}\n\n"
        f"⚠️ Переведите точную сумму. После перевода нажмите кнопку ниже."
    )
    await callback.message.edit_text(text, reply_markup=confirm_payment_kb(), parse_mode="Markdown")
    await state.set_state(OrderState.waiting_for_payment_confirm)

@dp.callback_query(OrderState.waiting_for_payment_confirm, F.data == "payment_done")
async def payment_done_check(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    # Уведомляем пользователя
    await callback.message.edit_text(
        "⏳ **Ваша заявка отправлена на проверку!**\n"
        "Менеджер проверит поступление средств и начислит звезды в течение нескольких минут.",
        reply_markup=main_menu_kb(),
        parse_mode="Markdown"
    )
    
    # Отправляем админу сообщение для подтверждения
    admin_text = (
        f"🔔 **Новая заявка на оплату (Сбербанк)!**\n\n"
        f"Пользователь: @{callback.from_user.username} (ID: {callback.from_user.id})\n"
        f"Кому звезды: {data['target_user']}\n"
        f"Количество: {data['amount']} ⭐\n"
        f"Сумма к получению: {data['price']} ₽\n\n"
        f"Проверьте банк на наличие перевода!"
    )
    
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=admin_text)
    except Exception as e:
        logging.error(f"Не удалось отправить уведомление админу: {e}")
        # Отправляем сообщение пользователю, что произошла ошибка
        await callback.message.answer(
            "⚠️ Произошла ошибка при отправке уведомления. Пожалуйста, сообщите администратору. @fyhjollyy",
            reply_markup=main_menu_kb()
        )
    
    await state.clear()

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
