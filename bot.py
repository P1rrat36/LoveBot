import os
import asyncio
import json
import logging
from datetime import date

from schedule_data import get_today_classes, get_current_week

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from dotenv import load_dotenv

from texts import (
    compliments, hugs, kisses, support,
    pick, days_together, pill_messages
)
from scheduler import start_scheduler, load_stats, save_stats, get_pill_kb

# Вмикаємо логування
logging.basicConfig(level=logging.INFO)

# ────── НАЛАШТУВАННЯ ──────
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

TOGETHER_DATE = date(2025, 11, 17)
SUBSCRIBERS_FILE = "subscribers.json"
OWNER_ID = 821454062  # ТИ

# ────── ІНІЦІАЛІЗАЦІЯ ──────
bot = Bot(
    BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()


# ────── ПІДПИСНИКИ ──────
def load_subscribers():
    try:
        with open(SUBSCRIBERS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_subscribers(data):
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(data, f)


subscribers = load_subscribers()

# ────── СТАТИСТИКА ──────
stats = load_stats()


def inc_stat(key: str):
    stats[key] = stats.get(key, 0) + 1
    stats["total_messages"] = stats.get("total_messages", 0) + 1


# ────── КЛАВІАТУРИ ──────
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🌸 Комплімент"), KeyboardButton(text="🤗 Обійми")],
        [KeyboardButton(text="💋 Поцілунок"), KeyboardButton(text="💌 Підтримка")],
        [KeyboardButton(text="🗓️ Дні разом"), KeyboardButton(text="🎓 Мої пари")],
        [KeyboardButton(text="💭 Настрій"), KeyboardButton(text="📊 Статистика")]
    ],
    resize_keyboard=True
)

mood_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🙂 Добре"), KeyboardButton(text="😔 Сумно")],
        [KeyboardButton(text="😴 Втомлена"), KeyboardButton(text="🥰 Щаслива")],
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)


# ────── /start ──────
@dp.message(CommandStart())
async def start(msg: types.Message):
    if msg.chat.id not in subscribers:
        subscribers.append(msg.chat.id)
        save_subscribers(subscribers)

    await msg.answer(
        "💖 Привіт, моя хороша…\nЯ завжди поруч з тобою 💋",
        reply_markup=main_keyboard
    )


# ────── ОБРОБКА КНОПОК ЛІКІВ (INLINE) ──────
@dp.callback_query(lambda c: c.data.startswith("taken|"))
async def pill_taken(callback: types.CallbackQuery):
    pill_name = callback.data.split("|")[1]

    await callback.message.edit_text(
        f"✅ Ти випила: <b>{pill_name}</b>\n\nМоя розумничка! Пишаюсь тобою, сонечко, і дуже люблю ❤️"
    )
    await callback.answer("Люблю тебе! 😘")
    await bot.send_message(OWNER_ID, f"💊 Кохана випила ліки: <b>{pill_name}</b>")


@dp.callback_query(lambda c: c.data.startswith("missed|"))
async def pill_missed(callback: types.CallbackQuery):
    pill_name = callback.data.split("|")[1]

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏳ Через 15 хв", callback_data=f"postpone|15|{pill_name}")],
        [InlineKeyboardButton(text="⏳ Через 30 хв", callback_data=f"postpone|30|{pill_name}")],
        [InlineKeyboardButton(text="⏳ Через 1 годину", callback_data=f"postpone|60|{pill_name}")]
    ])

    await callback.message.edit_text(
        f"🥺 Ти ще не випила <b>{pill_name}</b>...\nКоли мені тобі нагадати, котику?",
        reply_markup=kb
    )


@dp.callback_query(lambda c: c.data.startswith("postpone|"))
async def pill_postpone(callback: types.CallbackQuery):
    _, minutes_str, pill_name = callback.data.split("|")
    minutes = int(minutes_str)

    await callback.message.edit_text(
        f"⏳ Добре, сонечко! Нагадаю про <b>{pill_name}</b> через {minutes} хвилин 💋\nНе забудь!"
    )
    await callback.answer()
    asyncio.create_task(remind_later(callback.message.chat.id, pill_name, minutes))


async def remind_later(chat_id: int, pill_name: str, minutes: int):
    await asyncio.sleep(minutes * 60)
    msg_text = f"🔔 {pick(pill_messages)}\n\n💊 Нагадування про ліки: <b>{pill_name}</b>"
    await bot.send_message(chat_id, msg_text, reply_markup=get_pill_kb(pill_name))


# ────── ЛОГІКА КНОПОК ГОЛОВНОГО МЕНЮ ──────
@dp.message()
async def handle_buttons(msg: types.Message):
    text = msg.text

    if text == "🌸 Комплімент":
        await msg.answer(pick(compliments))
        inc_stat("compliments")

    elif text == "🤗 Обійми":
        await msg.answer(pick(hugs))
        inc_stat("hugs")

    elif text == "💋 Поцілунок":
        await msg.answer(pick(kisses))
        inc_stat("kisses")

    elif text == "💌 Підтримка":
        await msg.answer(pick(support))
        inc_stat("support")

    elif text == "💭 Настрій":
        await msg.answer("💭 Як ти сьогодні почуваєшся, моя хороша?", reply_markup=mood_keyboard)

    elif text in ["🙂 Добре", "😔 Сумно", "😴 Втомлена", "🥰 Щаслива"]:
        mood_answers = {
            "🙂 Добре": "Радий чути! 💛",
            "😔 Сумно": "Я поруч з тобою ❤️",
            "😴 Втомлена": "Відпочинь, моя радість 🌸",
            "🥰 Щаслива": "Твоя радість — і моя 💖"
        }
        await msg.answer(mood_answers[text], reply_markup=main_keyboard)
        await bot.send_message(OWNER_ID, f"💭 <b>Настрій коханої:</b>\n{text}\n\n⏰ {msg.date.strftime('%H:%M')}")
        inc_stat("mood")

    elif text == "⬅️ Назад":
        await msg.answer("💖 Я тут. Обери щось для себе ❤️", reply_markup=main_keyboard)
        stats["total_messages"] = stats.get("total_messages", 0) + 1

    elif text == "🗓️ Дні разом":
        await msg.answer(
            f"🗓️ Ми разом уже <b>{days_together(TOGETHER_DATE)} днів</b> 💞\nІ кожен день з тобою — неймовірний ✨")
        stats["total_messages"] = stats.get("total_messages", 0) + 1

    elif text == "📊 Статистика":
        await msg.answer(
            f"📊 <b>Наша статистика</b>\n\n"
            f"✉️ Повідомлень: {stats.get('total_messages', 0)}\n"
            f"🤗 Обіймів: {stats.get('hugs', 0)}\n"
            f"🌸 Компліментів: {stats.get('compliments', 0)}\n"
            f"💋 Поцілунків: {stats.get('kisses', 0)}\n"
            f"💌 Підтримки: {stats.get('support', 0)}"
        )

    elif text == "🎓 Мої пари":
        classes = get_today_classes()
        week = get_current_week()

        if not classes:
            await msg.answer(f"🎉 Котику, сьогодні ({week}-й тиждень) у тебе немає пар! Відпочивай і набирайся сил 💖")
        else:
            text_resp = f"📖 <b>Твій розклад на сьогодні ({week}-й тиждень):</b>\n\n"
            for c in classes:
                text_resp += (
                    f"⏰ <b>{c['time']}</b> — {c['subject']} ({c['type']})\n"
                    f"👩‍🏫 <i>{c['teacher']}</i>\n"
                    f"🔗 <a href='{c['link']}'>Підключитися</a>\n\n"
                )
            text_resp += "Я вірю в тебе, кохана! Гарного навчання 😘"
            await msg.answer(text_resp, disable_web_page_preview=True)

        stats["total_messages"] = stats.get("total_messages", 0) + 1

    # Зберігаємо статистику в самому кінці, незалежно від того, яку кнопку натиснуто
    save_stats(stats)


# ────── ЗАПУСК ──────
async def main():
    print("🚀 Бот успішно підключився і починає роботу...")
    asyncio.create_task(start_scheduler(bot, subscribers, stats))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())