Nfrimport os
import asyncio
import json
from datetime import date

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

from texts import (
    compliments, hugs, kisses, support,
    pick, days_together
)
from scheduler import start_scheduler, load_stats, save_stats

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
        [KeyboardButton(text="🗓️ Дні разом"), KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="💭 Настрій")]
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

# ────── ЛОГІКА КНОПОК ──────
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
        await msg.answer(
            "💭 Як ти сьогодні почуваєшся, моя хороша?",
            reply_markup=mood_keyboard
        )

    elif text in ["🙂 Добре", "😔 Сумно", "😴 Втомлена", "🥰 Щаслива"]:
        mood_answers = {
            "🙂 Добре": "Радий чути! 💛",
            "😔 Сумно": "Я поруч з тобою ❤️",
            "😴 Втомлена": "Відпочинь, моя радість 🌸",
            "🥰 Щаслива": "Твоя радість — і моя 💖"
        }

        # Відповідь їй
        await msg.answer(mood_answers[text], reply_markup=main_keyboard)

        # Повідомлення ТОБІ
        await bot.send_message(
            OWNER_ID,
            f"💭 <b>Настрій коханої:</b>\n{text}\n\n⏰ {msg.date.strftime('%H:%M')}"
        )

        inc_stat("mood")

    elif text == "⬅️ Назад":
        await msg.answer(
            "💖 Я тут. Обери щось для себе ❤️",
            reply_markup=main_keyboard
        )
        stats["total_messages"] = stats.get("total_messages", 0) + 1

    elif text == "🗓️ Дні разом":
        await msg.answer(
            f"🗓️ Ми разом уже <b>{days_together(TOGETHER_DATE)} днів</b> 💞\n"
            f"І кожен день з тобою — неймовірний ✨"
        )
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

    save_stats(stats)

# ────── ЗАПУСК ──────
async def main():
    asyncio.create_task(start_scheduler(bot, subscribers, stats))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())