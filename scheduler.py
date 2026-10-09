import asyncio
import random
import json
from datetime import datetime, time, timedelta
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo  # ДОДАНО: бібліотека для часових поясів
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from texts import morning_messages, evening_messages, random_love, daily_quotes, pick, pill_messages
from schedule_data import get_today_classes, get_current_week

STATS_FILE = "stats.json"
KYIV_TZ = ZoneInfo("Europe/Kyiv")  # ДОДАНО: встановлюємо Київський час


# ────── СТАТИСТИКА ──────
def load_stats():
    try:
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "total_messages": 0,
            "hugs": 0,
            "compliments": 0,
            "kisses": 0,
            "support": 0
        }


def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)


# ────── ДОПОМІЖНЕ ──────
def seconds_until(target: time):
    now = datetime.now(KYIV_TZ)  # ЗМІНЕНО: тепер беремо час по Києву
    target_dt = datetime.combine(now.date(), target, tzinfo=KYIV_TZ)  # ЗМІНЕНО: додаємо пояс до цільового часу

    if target_dt <= now:
        target_dt += timedelta(days=1)
    return (target_dt - now).total_seconds()


def pick_unique(array, sent_set):
    remaining = [m for m in array if m not in sent_set]
    if not remaining:
        sent_set.clear()
        remaining = array.copy()
    msg = random.choice(remaining)
    sent_set.add(msg)
    return msg


# ────── КЛАВІАТУРИ ДЛЯ ЛІКІВ ──────
def get_pill_kb(pill_name: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Випила", callback_data=f"taken|{pill_name}")],
        [InlineKeyboardButton(text="❌ Ще не випила", callback_data=f"missed|{pill_name}")]
    ])


# ────── НАГАДУВАННЯ ПРО ЛІКИ ──────
async def schedule_pill(bot, subscribers, hour, minute, pill_name):
    while True:
        await asyncio.sleep(seconds_until(time(hour, minute)))
        for user_id in subscribers:
            msg_text = f"{pick(pill_messages)}\n\n💊 Час випити: <b>{pill_name}</b>"
            await bot.send_message(user_id, msg_text, reply_markup=get_pill_kb(pill_name))
        await asyncio.sleep(60)


# ────── НАГАДУВАННЯ ПРО ПАРИ ──────
async def classes_reminder_task(bot, subscribers):
    while True:
        now = datetime.now(KYIV_TZ)
        today_classes = get_today_classes()

        for cls in today_classes:
            # Розбираємо час початку пари
            hour, minute = map(int, cls["time"].split(":"))
            class_time = datetime.combine(now.date(), time(hour, minute), tzinfo=KYIV_TZ)

            # Рахуємо різницю в хвилинах
            time_diff = (class_time - now).total_seconds() / 60

            # Якщо до пари залишилось від 9 до 10 хвилин - надсилаємо сповіщення
            if 9 <= time_diff <= 10:
                msg_text = (
                    f"🐰 Сонечко, через 10 хвилин почнеться пара!\n\n"
                    f"📚 <b>{cls['subject']}</b> ({cls['type']})\n"
                    f"👩‍🏫 Викладач: {cls['teacher']}\n"
                    f"⏰ Час: {cls['time']}\n\n"
                    f"🔗 <a href='{cls['link']}'>Посилання на підключення</a>\n\n"
                    f"Успіхів тобі, ти в мене найрозумніша! ❤️"
                )

                for user_id in subscribers:
                    await bot.send_message(user_id, msg_text, disable_web_page_preview=True)

        # Перевіряємо кожну хвилину
        await asyncio.sleep(60)

# ────── РАНОК 11:00 ──────
async def morning_task(bot, subscribers, stats):
    sent = set()
    while True:
        await asyncio.sleep(seconds_until(time(11, 0)))
        for user_id in subscribers:
            msg = pick_unique(morning_messages, sent)
            await bot.send_message(user_id, msg)
            stats["total_messages"] += 1
        save_stats(stats)
        await asyncio.sleep(60)  # захист від повтору


# ────── ВЕЧІР 01:00 (На добраніч) ──────
async def evening_task(bot, subscribers, stats):
    sent = set()
    while True:
        await asyncio.sleep(seconds_until(time(1, 0)))
        for user_id in subscribers:
            msg = pick_unique(evening_messages, sent)
            await bot.send_message(user_id, msg)
            stats["total_messages"] += 1
        save_stats(stats)
        await asyncio.sleep(60)


# ────── 5 РАНДОМНИХ ПОВІДОМЛЕНЬ ВДЕНЬ ──────
async def random_love_task(bot, subscribers, stats):
    while True:
        now = datetime.now(KYIV_TZ)  # ЗМІНЕНО
        start = datetime.combine(now.date(), time(10, 0), tzinfo=KYIV_TZ)  # ЗМІНЕНО
        end = datetime.combine(now.date(), time(22, 0), tzinfo=KYIV_TZ)  # ЗМІНЕНО

        if now >= end:
            await asyncio.sleep(seconds_until(time(10, 0)))
            continue

        total_seconds = (end - start).total_seconds()
        slots = sorted(random.sample(range(int(total_seconds)), 5))

        for offset in slots:
            target = start + timedelta(seconds=offset)
            wait = (target - datetime.now(KYIV_TZ)).total_seconds()  # ЗМІНЕНО
            if wait > 0:
                await asyncio.sleep(wait)

            for user_id in subscribers:
                await bot.send_message(user_id, pick(random_love))
                stats["total_messages"] += 1
            save_stats(stats)

        await asyncio.sleep(seconds_until(time(10, 0)))


# ────── ЩОДЕННА АФІРМАЦІЯ (12:00) ──────
async def daily_quote_task(bot, subscribers, stats):
    while True:
        await asyncio.sleep(seconds_until(time(12, 0)))
        for user_id in subscribers:
            await bot.send_message(user_id, pick(daily_quotes))
            stats["total_messages"] += 1
        save_stats(stats)
        await asyncio.sleep(60)


# ────── СТАРТ ПЛАНУВАЛЬНИКА ──────
# ────── СТАРТ ПЛАНУВАЛЬНИКА ──────
async def start_scheduler(bot, subscribers, stats):
    asyncio.create_task(morning_task(bot, subscribers, stats))
    asyncio.create_task(evening_task(bot, subscribers, stats))
    asyncio.create_task(random_love_task(bot, subscribers, stats))
    asyncio.create_task(daily_quote_task(bot, subscribers, stats))

    asyncio.create_task(schedule_pill(bot, subscribers, 22, 0, "Магній + Гідазепам"))
    asyncio.create_task(classes_reminder_task(bot, subscribers))
