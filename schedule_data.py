from datetime import datetime, date
from zoneinfo import ZoneInfo

KYIV_TZ = ZoneInfo("Europe/Kyiv")


# Функція для визначення поточного тижня за таблицею
def get_current_week():
    now = datetime.now(KYIV_TZ).date()
    week2_start = date(2026, 9, 7)

    if now < date(2026, 9, 1):
        return 0
    if now < week2_start:
        return 1

    # Вираховуємо тиждень: різниця в днях від початку 2-го тижня ділиться на 7
    return (now - week2_start).days // 7 + 2


# Розклад пар (0 - Понеділок, 1 - Вівторок ... 5 - Субота)
SCHEDULE = {
    0: [
        {"time": "08:00", "subject": "Управління комунікаціями...", "teacher": "Атанасов М. В.", "type": "Лекція",
         "weeks": range(2, 12), "link": "https://us05web.zoom.us/j/81993252228?pwd=HuyaoXkZFVEv9rHBakowE4bB5HAOOn.1"},
        {"time": "08:00", "subject": "Управління комунікаціями...", "teacher": "Атанасов М. В.", "type": "Практика",
         "weeks": range(12, 14), "link": "https://us05web.zoom.us/j/81993252228?pwd=HuyaoXkZFVEv9rHBakowE4bB5HAOOn.1"},
        {"time": "09:35", "subject": "Управління комунікаціями...", "teacher": "Атанасов М. В.", "type": "Практика",
         "weeks": range(3, 14), "link": "https://us05web.zoom.us/j/81993252228?pwd=HuyaoXkZFVEv9rHBakowE4bB5HAOOn.1"},
    ],
    1: [
        {"time": "08:00", "subject": "Кіберпсихологія", "teacher": "Тодорова М.М.", "type": "Лекція",
         "weeks": range(2, 11), "link": "https://us05web.zoom.us/j/7200211619?pwd=d003dEtkMElxSjFSVjRVZFJYRnM4UT09"},
        {"time": "08:00", "subject": "Кіберпсихологія", "teacher": "Тодорова М.М.", "type": "Практика",
         "weeks": range(11, 14), "link": "https://us05web.zoom.us/j/7200211619?pwd=d003dEtkMElxSjFSVjRVZFJYRnM4UT09"},
        {"time": "09:35", "subject": "Кіберпсихологія", "teacher": "Тодорова М.М.", "type": "Практика",
         "weeks": range(3, 14), "link": "https://us05web.zoom.us/j/7200211619?pwd=d003dEtkMElxSjFSVjRVZFJYRnM4UT09"},
        {"time": "11:10", "subject": "Клінічна психологія", "teacher": "Хозратулова І.A.", "type": "Лекція",
         "weeks": range(1, 14), "link": "https://us05web.zoom.us/j/5533634411?pwd=iPNpuHfk949wB2IxE1w3kNyXy6AB42.1"},
        {"time": "12:45", "subject": "Клінічна психологія", "teacher": "Хозратулова І.A.", "type": "Практика",
         "weeks": range(2, 14), "link": "https://us05web.zoom.us/j/5533634411?pwd=iPNpuHfk949wB2IxE1w3kNyXy6AB42.1"},
    ],
    2: [
        {"time": "08:00", "subject": "Кіберпсихологія", "teacher": "Тодорова М.М.", "type": "Практика",
         "weeks": range(3, 10), "link": "https://us05web.zoom.us/j/7200211619?pwd=d003dEtkMElxSjFSVjRVZFJYRnM4UT09"},
        {"time": "08:00", "subject": "Управління комунікаціями...", "teacher": "Атанасов М.В.", "type": "Практика",
         "weeks": range(8, 14), "link": "https://us05web.zoom.us/j/81993252228?pwd=HuyaoXkZFVEv9rHBakowE4bB5HAOOn.1"},
        {"time": "09:35", "subject": "Клінічна психологія", "teacher": "Хозратулова I.A.", "type": "Лекція",
         "weeks": range(1, 4), "link": "https://us05web.zoom.us/j/5533634411?pwd=iPNpuHfk949wB2IxE1w3kNyXy6AB42.1"},
        {"time": "09:35", "subject": "Клінічна психологія", "teacher": "Хозратулова I.A.", "type": "Практика",
         "weeks": range(4, 9), "link": "https://us05web.zoom.us/j/5533634411?pwd=iPNpuHfk949wB2IxE1w3kNyXy6AB42.1"},
    ],
    3: [
        {"time": "09:35", "subject": "Управління карʼєрою та лідерство", "teacher": "Калугіна Н.А.", "type": "Лекція",
         "weeks": range(1, 11), "link": "https://us04web.zoom.us/j/9525242777?pwd=UFpRRTJFbGVsZC8vVENjWUZycEc2QT09"},
        {"time": "09:35", "subject": "Управління карʼєрою та лідерство", "teacher": "Калугіна Н.А.", "type": "Практика",
         "weeks": range(11, 14), "link": "https://us04web.zoom.us/j/9525242777?pwd=UFpRRTJFbGVsZC8vVENjWUZycEc2QT09"},
        {"time": "11:10", "subject": "Управління карʼєрою та лідерство", "teacher": "Калугіна H.A.", "type": "Практика",
         "weeks": range(2, 14), "link": "https://us04web.zoom.us/j/9525242777?pwd=UFpRRTJFbGVsZC8vVENjWUZycEc2QT09"},
        {"time": "12:45", "subject": "Управління карʼєрою та лідерство", "teacher": "Калугіна Н.А.", "type": "Практика",
         "weeks": range(2, 7), "link": "https://us04web.zoom.us/j/9525242777?pwd=UFpRRTJFbGVsZC8vVENjWUZycEc2QT09"},
    ],
    4: [],  # П'ятниця вихідний
    5: [
        {"time": "08:00", "subject": "Вступ в поліграфологію", "teacher": "Здебський Д.В.", "type": "Лекція",
         "weeks": range(1, 11), "link": "https://us05web.zoom.us/j/6832039286?pwd=Bh17qZkccybu6YJKIiAYVHGrVBSsem.1"},
        {"time": "08:00", "subject": "Вступ в поліграфологію", "teacher": "Здебський Д.В.", "type": "Практика",
         "weeks": range(11, 14), "link": "https://us05web.zoom.us/j/6832039286?pwd=Bh17qZkccybu6YJKIiAYVHGrVBSsem.1"},
        {"time": "09:35", "subject": "Вступ в поліграфологію", "teacher": "Здебський Д.В.", "type": "Практика",
         "weeks": range(2, 14), "link": "https://us05web.zoom.us/j/6832039286?pwd=Bh17qZkccybu6YJKIiAYVHGrVBSsem.1"},
        {"time": "11:10", "subject": "Вступ в поліграфологію", "teacher": "Здебський Д.В.", "type": "Практика",
         "weeks": range(2, 7), "link": "https://us05web.zoom.us/j/6832039286?pwd=Bh17qZkccybu6YJKIiAYVHGrVBSsem.1"},
    ],
    6: []  # Неділя вихідний
}


def get_today_classes():
    week = get_current_week()
    weekday = datetime.now(KYIV_TZ).weekday()

    if weekday not in SCHEDULE:
        return []

    today_classes = []
    for cls in SCHEDULE[weekday]:
        if week in cls["weeks"]:
            today_classes.append(cls)

    # Сортуємо по часу на випадок збою порядку
    return sorted(today_classes, key=lambda x: x["time"])