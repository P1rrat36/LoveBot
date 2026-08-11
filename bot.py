import asyncio
import random
import json
from datetime import datetime, time, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from texts import morning_messages, evening_messages, random_love, daily_quotes, pick, pill_messages

STATS_FILE = "stats.json"


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
    now = datetime.now()
    target_dt = datetime.combine(now.date(), target)
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
        now = datetime.now()
        start = datetime.combine(now.date(), time(10, 0))
        end = datetime.combine(now.date(), time(22, 0))

        if now >= end:
            await asyncio.sleep(seconds_until(time(10, 0)))
            continue

        total_seconds = (end - start).total_seconds()
        slots = sorted(random.sample(range(int(total_seconds)), 5))

        for offset in slots:
            target = start + timedelta(seconds=offset)
            wait = (target - datetime.now()).total_seconds()
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
async def start_scheduler(bot, subscribers, stats):
    asyncio.create_task(morning_task(bot, subscribers, stats))
    asyncio.create_task(evening_task(bot, subscribers, stats))
    asyncio.create_task(random_love_task(bot, subscribers, stats))
    asyncio.create_task(daily_quote_task(bot, subscribers, stats))

    # --- Нагадування про ліки рівно по годинах ---
    asyncio.create_task(schedule_pill(bot, subscribers, 12, 0, "Вітамін Є (день)"))
    asyncio.create_task(schedule_pill(bot, subscribers, 20, 0, "Вітамін Є (вечір)"))
    asyncio.create_task(schedule_pill(bot, subscribers, 22, 0, "Магній + Гідазепам"))