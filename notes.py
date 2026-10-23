# -*- coding: utf-8 -*-
"""Заметки 3.0 — доска заметок по дням: календарь, напоминания, Яндекс.Календарь.

Запуск:            pythonw notes.py
В трее при старте: pythonw notes.py --tray
Ярлык на столе:    python notes.py --make-shortcut
Самопроверка:      python notes.py --selftest [папка]
Сборка:            python notes.py --build
"""
import sys
import os
import json
import uuid
import time
import math
import random
import base64
import hashlib
import shutil
import subprocess
import traceback
from datetime import datetime, timedelta, date as pydate
from string import Template
from typing import NoReturn

APP_VERSION = "3.0"
FROZEN = bool(getattr(sys, "frozen", False))
APP_DIR = (os.path.dirname(sys.executable) if FROZEN
           else os.path.dirname(os.path.abspath(__file__)))
HOME = os.path.expanduser("~")
DATA_FILE = os.path.join(HOME, ".stickies_data.json")
CONFIG_FILE = os.path.join(HOME, ".stickies_config.json")
def _find_icon():
    roots = [APP_DIR, getattr(sys, "_MEIPASS", APP_DIR)]
    for root in roots:
        for name in ("notes.ico", "stickies.ico"):
            path = os.path.join(root, name)
            if os.path.exists(path):
                return path
    return os.path.join(APP_DIR, "notes.ico")


ICON_FILE = _find_icon()
LOG_FILE = os.path.join(APP_DIR, "stickies.log")
YANDEX_URL = "https://caldav.yandex.ru/"

NOTE_W, NOTE_H = 240, 206
NOTE_MIN_W, NOTE_MIN_H = 180, 130
# поля «бумаги» внутри виджета стикера (сверху — место для скотча)
PAPER_L, PAPER_T, PAPER_R, PAPER_B = 4, 11, 4, 5

DEFAULT_MORNING = "10:00"
DEFAULT_EVENING = "17:00"
DEFAULT_PLAN_TIME = "20:00"
SNOOZE_MINUTES = 10


# ============================== ЯЗЫК ====================================
LANG = "ru"

STR = {
    "app": ("Заметки", "Notes"),
    "search": ("Поиск по всем заметкам", "Search all notes"),
    "prev_month": ("Предыдущий месяц", "Previous month"),
    "next_month": ("Следующий месяц", "Next month"),
    "found": ("НАЙДЕНО", "FOUND"),
    "nothing_found": ("Ничего не найдено", "Nothing found"),
    "archive_suffix": (" · архив", " · done"),
    "carry_btn": ("Незавершённое — на сегодня", "Unfinished → today"),
    "carry_tip": ("Перенести незавершённые заметки из прошлых дней на сегодня",
                  "Move unfinished notes from past days to today"),
    "settings": ("Настройки", "Settings"),
    "dark_theme": ("Тёмная тема", "Dark theme"),
    "light_theme": ("Светлая тема", "Light theme"),
    "prev_day": ("Предыдущий день (Alt+←)", "Previous day (Alt+←)"),
    "next_day": ("Следующий день (Alt+→)", "Next day (Alt+→)"),
    "today": ("Сегодня", "Today"),
    "today_tip": ("Перейти к сегодняшнему дню (Ctrl+T)", "Go to today (Ctrl+T)"),
    "tomorrow": ("Завтра", "Tomorrow"),
    "yesterday": ("Вчера", "Yesterday"),
    "mark_today": ("СЕГОДНЯ", "TODAY"),
    "mark_tomorrow": ("ЗАВТРА", "TOMORROW"),
    "mark_yesterday": ("ВЧЕРА", "YESTERDAY"),
    "new_note": ("Новая заметка", "New note"),
    "new_note_tip": ("Ctrl+N или двойной щелчок по доске",
                     "Ctrl+N or double-click the board"),
    "tidy": ("Упорядочить", "Tidy up"),
    "tidy_tip": ("Разложить заметки ровными рядами", "Arrange notes in neat rows"),
    "yandex": ("Яндекс.Календарь", "Yandex Calendar"),
    "yandex_tip": ("Загрузить события этого дня из Яндекс.Календаря",
                   "Import this day's events from Yandex Calendar"),
    "undo": ("Отменить", "Undo"),
    "undo_tip": ("Вернуть последнюю убранную заметку (Ctrl+Z)",
                 "Bring back the last removed note (Ctrl+Z)"),
    "archive": ("Архив", "Done"),
    "archive_tip": ("Показать выполненные заметки этого дня",
                    "Show this day's completed notes"),
    "done_title": ("Выполнено", "Completed"),
    "archive_empty": ("Выполненные заметки этого дня появятся здесь.",
                      "Completed notes for this day will appear here."),
    "restore": ("Вернуть", "Restore"),
    "delete": ("Удалить", "Delete"),
    "empty": ("(пусто)", "(empty)"),
    "no_notes": ("Заметок нет", "No notes"),
    "n_done": ("{n} выполнено", "{n} done"),
    "empty_quote": ("Красота — в мелочах", "There is beauty in small things"),
    "empty_hint": ("Дважды щёлкните по доске или нажмите Ctrl+N",
                   "Double-click the board or press Ctrl+N"),
    "placeholder": ("Заметка…", "Note…"),
    "tag_yandex": ("ЯНДЕКС", "YANDEX"),
    "tag_yandex_tip": ("Событие из Яндекс.Календаря", "Event from Yandex Calendar"),
    "tag_plan": ("ОБЯЗАТЕЛЬНО", "DAILY"),
    "tag_plan_tip": ("Ежедневная обязательная заметка", "Daily required note"),
    "plan_text": ("Заполнить заметки на завтра", "Fill in tomorrow's notes"),
    "btn_more": ("Цвет и действия", "Colour and actions"),
    "btn_done": ("Выполнено — в архив", "Done — move to archive"),
    "btn_delete": ("Удалить", "Delete"),
    "btn_bell": ("Напоминание", "Reminder"),
    "grip": ("Потяните, чтобы изменить размер", "Drag to resize"),
    "m_color": ("Цвет", "Colour"),
    "m_reminder": ("Напоминание…", "Reminder…"),
    "m_duplicate": ("Дублировать", "Duplicate"),
    "m_repeat": ("Повторять…", "Repeat…"),
    "rep_title": ("Повторять заметку", "Repeat note"),
    "rep_none": ("Не повторять", "Don't repeat"),
    "rep_daily": ("Каждый день", "Every day"),
    "rep_weekdays": ("По будням", "On weekdays"),
    "rep_days": ("По дням недели", "On these days"),
    "rep_monthly": ("Каждый месяц, {n} числа", "Every month on the {n}"),
    "rep_hint": ("Заметка будет сама появляться на доске в выбранные дни. Начало "
                 "повтора: {d}. Напоминание, если оно есть, повторится вместе с ней.",
                 "The note will appear on the board on the chosen days, starting "
                 "{d}. Its reminder, if any, repeats too."),
    "rep_txt_daily": ("каждый день", "every day"),
    "rep_txt_weekdays": ("по будням", "weekdays"),
    "rep_txt_monthly": ("{n} числа", "monthly, {n}"),
    "btn_repeat": ("Повторяется", "Repeats"),
    "m_move_today": ("Перенести на сегодня", "Move to today"),
    "m_move_to": ("Перенести на другой день…", "Move to another day…"),
    "m_open_tomorrow": ("Открыть завтрашний день", "Open tomorrow"),
    "moved_to": ("Перенесено: {d}", "Moved to {d}"),
    "carried": ("Перенесено на сегодня: {n}", "Moved to today: {n}"),
    "carry_q": ("Перенести {n} {w} из прошлых дней на сегодня?",
                "Move {n} {w} from past days to today?"),
    "move_title": ("Перенести заметку", "Move note"),
    "move_hint": ("Выберите день, куда перенести заметку",
                  "Choose the day to move the note to"),
    "move_btn": ("Перенести", "Move"),
    "cancel": ("Отмена", "Cancel"),
    "save": ("Сохранить", "Save"),
    "q_day_after": ("Послезавтра", "Day after"),
    "q_monday": ("Понедельник", "Monday"),
    "q_week": ("Через неделю", "In a week"),
    "rem_title": ("Напоминание", "Reminder"),
    "rem_twice": ("Дважды в день", "Twice a day"),
    "rem_once": ("Один раз", "Once"),
    "rem_off": ("Без напоминания", "No reminder"),
    "rem_morning": ("Утром", "Morning"),
    "rem_evening": ("Вечером", "Evening"),
    "rem_at": ("В", "At"),
    "rem_hint_twice": ("Уведомление появится внизу справа дважды в день, "
                       "пока заметка не выполнена.",
                       "A notification will pop up at the bottom right twice a day "
                       "until the note is done."),
    "rem_hint_after12": ("Заметка создана после 12:00 — сегодня одно напоминание.",
                         "The note was created after 12:00, so one reminder today."),
    "rem_hint_day": ("Напоминания сработают в день заметки: {d}.",
                     "Reminders will fire on the note's day: {d}."),
    "popup_title": ("Напоминание", "Reminder"),
    "popup_done": ("Готово", "Done"),
    "popup_snooze": ("Через {n} мин", "In {n} min"),
    "popup_open": ("Открыть", "Open"),
    "popup_close": ("Закрыть", "Close"),
    "set_title": ("Настройки", "Settings"),
    "set_look": ("Внешний вид", "Appearance"),
    "set_lang": ("Язык", "Language"),
    "set_theme": ("Тема", "Theme"),
    "theme_light": ("Светлая", "Light"),
    "theme_dark": ("Тёмная", "Dark"),
    "set_palette": ("Палитра стикеров", "Sticker palette"),
    "set_font": ("Шрифт стикеров", "Sticker font"),
    "font_g_hand": ("РУКОПИСНЫЕ", "HANDWRITTEN"),
    "font_g_serif": ("С ЗАСЕЧКАМИ", "SERIF"),
    "font_g_sans": ("ПРОСТЫЕ", "SANS-SERIF"),
    "font_g_mono": ("МОНОШИРИННЫЕ", "MONOSPACED"),
    "font_other": ("Другой…", "Other…"),
    "set_preview": ("Так будет выглядеть заметка.\nКрасота — в мелочах.",
                    "This is how a note will look.\nThere is beauty in small things."),
    "set_flowers": ("Сухоцвет на доске", "Dried flowers on the board"),
    "set_reminders": ("Напоминания", "Reminders"),
    "set_morning": ("Утреннее", "Morning"),
    "set_evening": ("Вечернее", "Evening"),
    "set_plan": ("Обязательная заметка", "Daily required note"),
    "set_plan_hint": ("Каждый будний день и в воскресенье на доске появляется "
                      "заметка «Заполнить заметки на завтра» с напоминанием.",
                      "Every weekday and on Sunday the note \"Fill in tomorrow's "
                      "notes\" appears on the board with a reminder."),
    "set_yandex": ("Яндекс.Календарь", "Yandex Calendar"),
    "set_yandex_info": ("Укажите логин Яндекс ID и пароль приложения. Создать пароль "
                        "приложения можно на странице {link}.",
                        "Enter your Yandex ID login and an app password. You can create "
                        "an app password at {link}."),
    "set_login": ("Логин", "Login"),
    "set_password": ("Пароль приложения", "App password"),
    "set_system": ("Система", "System"),
    "set_autostart": ("Запускать при входе в систему (свёрнутым в трей)",
                      "Start at login (minimised to tray)"),
    "set_shortcut": ("Создать ярлык на рабочем столе", "Create desktop shortcut"),
    "shortcut_ok": ("Ярлык «{name}» создан на рабочем столе.",
                    "Shortcut \"{name}\" created on the desktop."),
    "shortcut_only_win": ("На Mac перетащите Notes.app в папку «Программы» — оттуда "
                          "приложение запускается из Launchpad и Spotlight.",
                          "On a Mac, drag Notes.app into Applications to launch it from "
                          "Launchpad and Spotlight."),
    "shortcut_ok_linux": ("«{name}» добавлены в меню приложений и на рабочий стол.",
                          "\"{name}\" was added to the app menu and the desktop."),
    "shortcut_fail": ("Не удалось создать ярлык.", "Could not create the shortcut."),
    "shortcut_desc": ("Заметки по дням", "Day-by-day notes"),
    "autostart_fail": ("Не удалось изменить автозапуск:\n{e}",
                       "Could not change autostart:\n{e}"),
    "y_need_login": ("Сначала укажите логин и пароль приложения в настройках.",
                     "Enter your login and app password in Settings first."),
    "y_loading": ("Загружаю события из Яндекс.Календаря…",
                  "Loading events from Yandex Calendar…"),
    "y_result": ("Событий получено: {n}, добавлено новых: {a}",
                 "Events received: {n}, new added: {a}"),
    "y_fail": ("Не удалось загрузить события:\n\n{e}", "Could not load events:\n\n{e}"),
    "no_title": ("(без названия)", "(untitled)"),
    "tray_open": ("Открыть", "Open"),
    "tray_new": ("Новая заметка на сегодня", "New note for today"),
    "tray_quit": ("Выход", "Quit"),
    "tray_notice": ("Приложение продолжает работать в трее. Выход — через меню значка.",
                    "The app keeps running in the tray. Quit from the tray icon menu."),
    "no_pyside": ("Не найдена библиотека PySide6.\n\nУстановите зависимости командой:\n"
                  "pip install PySide6 caldav icalendar",
                  "PySide6 was not found.\n\nInstall the dependencies with:\n"
                  "pip install PySide6 caldav icalendar"),
}

MONTHS_GEN = {
    "ru": ["января", "февраля", "марта", "апреля", "мая", "июня", "июля",
           "августа", "сентября", "октября", "ноября", "декабря"],
    "en": ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"],
}
MONTHS_NOM = {
    "ru": ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль",
           "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"],
    "en": MONTHS_GEN["en"],
}
WEEKDAYS = {
    "ru": ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница",
           "Суббота", "Воскресенье"],
    "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
           "Saturday", "Sunday"],
}
WEEKDAYS_SHORT = {
    "ru": ["пн", "вт", "ср", "чт", "пт", "сб", "вс"],
    "en": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
}
FORMS = {
    "note": (("заметка", "заметки", "заметок"), ("note", "notes")),
    "note_acc": (("заметку", "заметки", "заметок"), ("note", "notes")),
}


def set_language(code):
    global LANG
    LANG = code if code in ("ru", "en") else "ru"


def T(key, **kw):
    pair = STR.get(key)
    if pair is None:
        return key
    text = pair[0] if LANG == "ru" else pair[1]
    return text.format(**kw) if kw else text


def plural_ru(n, one, few, many):
    """1 заметка, 2 заметки, 5 заметок."""
    n = abs(int(n))
    if n % 10 == 1 and n % 100 != 11:
        return one
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return few
    return many


def word(n, key):
    ru, en = FORMS[key]
    if LANG == "ru":
        return plural_ru(n, *ru)
    return en[0] if abs(int(n)) == 1 else en[1]


def count_text(n, key="note"):
    return f"{n} {word(n, key)}"


def day_month(d, with_year=False):
    if LANG == "ru":
        text = f"{d.day} {MONTHS_GEN['ru'][d.month - 1]}"
        return text + (f" {d.year}" if with_year else "")
    text = f"{MONTHS_GEN['en'][d.month - 1]} {d.day}"
    return text + (f", {d.year}" if with_year else "")


def human_date(d, today=None):
    today = today or pydate.today()
    delta = (d - today).days
    if delta == 0:
        return T("today")
    if delta == 1:
        return T("tomorrow")
    if delta == -1:
        return T("yesterday")
    if d.year != today.year:
        return day_month(d, True)
    return f"{day_month(d)}, {WEEKDAYS_SHORT[LANG][d.weekday()]}"


def human_date_inline(d, today=None):
    """Дата внутри фразы: «завтра», «5 ноября, ср»."""
    text = human_date(d, today)
    return text[:1].lower() + text[1:] if LANG == "ru" else text


# ============================== ЛОГИКА ==================================
def parse_key(key):
    try:
        return datetime.strptime(key, "%Y-%m-%d").date()
    except Exception:
        return None


def parse_dt(text):
    try:
        return datetime.fromisoformat(str(text))
    except Exception:
        return None


def parse_hm(text):
    try:
        h, m = str(text).strip().split(":")[:2]
        h, m = int(h), int(m)
        if 0 <= h < 24 and 0 <= m < 60:
            return h, m
    except Exception:
        pass
    return None


def fmt_hm(h, m):
    return f"{int(h):02d}:{int(m):02d}"


def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("Load error:", path, e)
        return default


def save_json_atomic(path, obj):
    """Пишет во временный файл и подменяет им основной — данные не бьются."""
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
            f.flush()
            try:
                os.fsync(f.fileno())
            except OSError:
                pass
        os.replace(tmp, path)
        return True
    except Exception as e:
        print("Save error:", path, e)
        return False


def load_config():
    cfg = load_json(CONFIG_FILE, {})
    return cfg if isinstance(cfg, dict) else {}


def save_config(cfg):
    save_json_atomic(CONFIG_FILE, cfg)


def _to_int(value, default):
    try:
        return int(float(value))
    except Exception:
        return default


# ------------------------------ Палитры ---------------------------------
# Индексы цветов одинаковы во всех палитрах: 0 светлый, 1 тёплый, 2 холодный,
# 3 зелёный, 4 розовый, 5 сиреневый, 6 нейтральный. Заметка хранит индекс,
# поэтому смена палитры перекрашивает все стикеры сразу.
PALETTES = {
    "kraft": {
        "name": ("Крафт и бумага", "Kraft & paper"),
        "colors": ["#F2EADA", "#DCC39C", "#D5DBD6", "#D4D8BE",
                   "#EAD3C6", "#DDD4D8", "#EFE7D4"],
        "names": (["Сливки", "Крафт", "Туман", "Шалфей", "Пудра", "Вереск", "Клетка"],
                  ["Cream", "Kraft", "Mist", "Sage", "Powder", "Heather", "Grid"]),
        "grid": 6,
    },
    "pastel": {
        "name": ("Пастель", "Pastel"),
        "colors": ["#F6E7A1", "#F4CFA8", "#C5DBF0", "#CFE5C6",
                   "#EFC9D3", "#D9D0EC", "#F3EAD3"],
        "names": (["Лимон", "Персик", "Небо", "Мята", "Роза", "Лаванда", "Крем"],
                  ["Lemon", "Peach", "Sky", "Mint", "Rose", "Lavender", "Cream"]),
    },
    "nature": {
        "name": ("Природа", "Nature"),
        "colors": ["#EADDB4", "#E3B99C", "#CAD7D8", "#C5D0AB",
                   "#E7C5B7", "#D0C7D6", "#E9E4D4"],
        "names": (["Пшеница", "Терракота", "Иней", "Мох", "Глина", "Чабрец", "Лён"],
                  ["Wheat", "Terracotta", "Frost", "Moss", "Clay", "Thyme", "Linen"]),
    },
    "classic": {
        "name": ("Классика", "Classic"),
        "colors": ["#FFF27A", "#FFC58A", "#A9D8F5", "#B7E4A8",
                   "#F9B4C0", "#D3C0F0", "#FFFDF5"],
        "names": (["Жёлтый", "Оранжевый", "Голубой", "Зелёный", "Розовый",
                   "Сиреневый", "Белый"],
                  ["Yellow", "Orange", "Blue", "Green", "Pink", "Lilac", "White"]),
    },
}
PALETTE_ORDER = ["kraft", "pastel", "nature", "classic"]
DEFAULT_PALETTE = "kraft"
YANDEX_CI = 2
PLAN_CI = 0

# цвета прежних версий -> индекс
_LEGACY = {
    "#FFF9A6": 0, "#FFD6A5": 1, "#BDE0FE": 2, "#C8F7C5": 3, "#F8C8DC": 4,
    "#E0D3F5": 5, "#FFF1B8": 6,
}


def _rgb(hex_color):
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def color_index(hex_color):
    """Индекс палитры для цвета из старой версии (или ближайший по оттенку)."""
    if not isinstance(hex_color, str) or not hex_color.startswith("#") \
            or len(hex_color) != 7:
        return 0
    up = hex_color.upper()
    if up in _LEGACY:
        return _LEGACY[up]
    for pal in PALETTES.values():
        for i, c in enumerate(pal["colors"]):
            if c.upper() == up:
                return i
    try:
        r, g, b = _rgb(up)
    except Exception:
        return 0
    best, best_d = 0, None
    for i, c in enumerate(PALETTES["pastel"]["colors"]):
        cr, cg, cb = _rgb(c)
        d = (r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2
        if best_d is None or d < best_d:
            best, best_d = i, d
    return best


def palette_color(palette, ci):
    pal = PALETTES.get(palette) or PALETTES[DEFAULT_PALETTE]
    colors = pal["colors"]
    return colors[ci % len(colors)]


def palette_names(palette):
    pal = PALETTES.get(palette) or PALETTES[DEFAULT_PALETTE]
    return pal["names"][0 if LANG == "ru" else 1]


# ------------------------------ Заметки ---------------------------------
def normalize_note(item):
    """Приводит заметку из файла к полному виду. None — если это не заметка."""
    if not isinstance(item, dict):
        return None
    note = dict(item)
    note["id"] = str(note.get("id") or uuid.uuid4())
    note["x"] = max(0, _to_int(note.get("x"), 28))
    note["y"] = max(0, _to_int(note.get("y"), 28))
    note["w"] = max(NOTE_MIN_W, _to_int(note.get("w"), NOTE_W))
    note["h"] = max(NOTE_MIN_H, _to_int(note.get("h"), NOTE_H))
    text = note.get("text")
    note["text"] = text if isinstance(text, str) else ("" if text is None else str(text))
    ci = note.get("ci")
    if not isinstance(ci, int) or isinstance(ci, bool) or not 0 <= ci < 7:
        ci = color_index(note.get("color"))
    note["ci"] = ci
    if not isinstance(note.get("color"), str):
        note["color"] = PALETTES["pastel"]["colors"][ci]
    remind = note.get("remind")
    if remind is not None:
        times = []
        if isinstance(remind, dict):
            times = [fmt_hm(*hm) for hm in map(parse_hm, remind.get("times") or []) if hm]
        if times:
            remind = dict(remind)
            remind["times"] = sorted(set(times))
            note["remind"] = remind
        else:
            note.pop("remind", None)
    if not isinstance(note.get("fired"), list):
        note.pop("fired", None)
    return note


def normalize_data(raw, today_key):
    """Понимает все прежние форматы файла и возвращает {дата: {active, archived}}."""
    if isinstance(raw, list):
        raw = {today_key: {"active": raw, "archived": []}}
    elif isinstance(raw, dict) and isinstance(raw.get("active"), list):
        raw = {today_key: {"active": raw["active"],
                           "archived": raw.get("archived") or []}}
    if not isinstance(raw, dict):
        return {}
    days = {}
    for key, day in raw.items():
        if not isinstance(day, dict):
            continue
        active = [n for n in map(normalize_note, day.get("active") or []) if n]
        archived = [n for n in map(normalize_note, day.get("archived") or []) if n]
        days[str(key)] = {"active": active, "archived": archived}
    return days


def rects_of(items):
    return [(n.get("x", 0), n.get("y", 0), n.get("w", NOTE_W), n.get("h", NOTE_H))
            for n in items]


def find_free_spot(rects, w, h, avail_w, margin=28, gap=18):
    """Самое верхнее (затем левое) свободное место на доске.

    Кандидаты — левый/верхний край доски и края уже лежащих заметок, поэтому
    находятся и промежутки между заметками, а обычная раскладка выходит ровной.
    """
    avail_w = max(_to_int(avail_w, 0), w + 2 * margin)
    max_x = avail_w - margin - w

    def is_free(x, y):
        for rx, ry, rw, rh in rects:
            if (x < rx + rw + gap and rx < x + w + gap
                    and y < ry + rh + gap and ry < y + h + gap):
                return False
        return True

    xs = sorted({margin} | {rx + rw + gap for rx, ry, rw, rh in rects})
    ys = sorted({margin} | {ry + rh + gap for rx, ry, rw, rh in rects})
    for y in ys:
        for x in xs:
            if x <= max_x and is_free(x, y):
                return x, y
    bottom = max((ry + rh for rx, ry, rw, rh in rects), default=0)
    return margin, max(margin, bottom + gap)


def flow_layout(sizes, avail_w, margin=28, gap=18):
    """Раскладывает заметки рядами. sizes: [(w, h)] -> [(x, y)]."""
    avail_w = max(_to_int(avail_w, 0), 2 * margin + NOTE_MIN_W)
    out = []
    x, y, row_h = margin, margin, 0
    for w, h in sizes:
        if x > margin and x + w > avail_w - margin:
            x = margin
            y += row_h + gap
            row_h = 0
        out.append((x, y))
        x += w + gap
        row_h = max(row_h, h)
    return out


# --------------------------- Напоминания --------------------------------
def default_reminder(note_day, created, now, morning, evening):
    """Режим напоминания по умолчанию.

    Дважды в день (утро и вечер). Если заметка создана в свой день после 12:00 —
    одно напоминание: вечером, а если вечер уже прошёл — примерно через час.
    Возвращает ("twice", [утро, вечер]) или ("once", [время]).
    """
    created = created or now
    eh, em = parse_hm(evening) or (17, 0)
    if created.date() == note_day and created.hour >= 12:
        ev_dt = datetime.combine(note_day, datetime.min.time()).replace(hour=eh, minute=em)
        if note_day == now.date() and ev_dt <= now:
            soon = now + timedelta(hours=1)
            soon = soon.replace(minute=(soon.minute // 5) * 5, second=0, microsecond=0)
            if soon.date() != now.date():
                soon = now.replace(hour=23, minute=55, second=0, microsecond=0)
            return "once", [fmt_hm(soon.hour, soon.minute)]
        return "once", [fmt_hm(eh, em)]
    mh, mm = parse_hm(morning) or (10, 0)
    return "twice", sorted({fmt_hm(mh, mm), fmt_hm(eh, em)})


def due_reminders(note, day_key, now, window_hours=12):
    """Какие напоминания заметки пора показать.

    Срабатывают только в день самой заметки, только для времени после момента
    установки напоминания и не позже чем через 12 часов после срока.
    Возвращает (ключи «дата время» для отметки о показе, сработало ли «отложить»).
    """
    remind = note.get("remind")
    if not isinstance(remind, dict):
        return [], False
    if day_key != now.date().isoformat():
        return [], False
    since = parse_dt(remind.get("since")) or datetime.min
    fired = set(note.get("fired") or [])
    due = []
    day = now.date()
    for t in sorted(set(remind.get("times") or [])):
        hm = parse_hm(t)
        if not hm:
            continue
        at = datetime.combine(day, datetime.min.time()).replace(hour=hm[0], minute=hm[1])
        key = f"{day_key} {fmt_hm(*hm)}"
        if since < at <= now and now - at <= timedelta(hours=window_hours) \
                and key not in fired:
            due.append(key)
    snooze = parse_dt(remind.get("snooze"))
    snoozed = bool(snooze and snooze <= now)
    return due, snoozed


def prune_fired(fired, day_key):
    return [f for f in fired if str(f).startswith(day_key)][-12:]


def normalize_rule(rule):
    """Правило повтора или None, если оно некорректно."""
    if not isinstance(rule, dict):
        return None
    kind = rule.get("kind")
    if kind in ("daily", "weekdays"):
        return {"kind": kind}
    if kind == "days":
        days = sorted({int(d) for d in rule.get("days") or []
                       if isinstance(d, (int, float)) and 0 <= int(d) <= 6})
        return {"kind": "days", "days": days} if days else None
    if kind == "monthly":
        dom = _to_int(rule.get("dom"), 0)
        return {"kind": "monthly", "dom": dom} if 1 <= dom <= 31 else None
    return None


def rule_matches(rule, day):
    rule = normalize_rule(rule)
    if rule is None:
        return False
    kind = rule["kind"]
    if kind == "daily":
        return True
    if kind == "weekdays":
        return day.weekday() < 5
    if kind == "days":
        return day.weekday() in rule["days"]
    # каждый месяц; 31-е в коротком месяце — в последний день месяца
    nxt = (day.replace(day=28) + timedelta(days=4)).replace(day=1)
    last = (nxt - timedelta(days=1)).day
    return day.day == min(rule["dom"], last)


def rule_text(rule):
    rule = normalize_rule(rule)
    if rule is None:
        return ""
    kind = rule["kind"]
    if kind == "daily":
        return T("rep_txt_daily")
    if kind == "weekdays":
        return T("rep_txt_weekdays")
    if kind == "days":
        days = [int(d) for d in rule.get("days") or []]
        if days == [0, 1, 2, 3, 4]:
            return T("rep_txt_weekdays")
        if len(days) == 7:
            return T("rep_txt_daily")
        return ", ".join(WEEKDAYS_SHORT[LANG][d] for d in days)
    return T("rep_txt_monthly", n=rule["dom"])


def normalize_template(t):
    if not isinstance(t, dict) or not t.get("id"):
        return None
    rule = normalize_rule(t.get("rule"))
    if rule is None or not parse_key(str(t.get("start", ""))):
        return None
    out = dict(t)
    out["rule"] = rule
    out["skip"] = [k for k in (t.get("skip") or []) if isinstance(k, str)][-200:]
    return out


def plan_needed(day, plan_days):
    """Обязательная заметка нужна в будни и в воскресенье (не в субботу)."""
    return day.weekday() != 5 and day.isoformat() not in (plan_days or [])


class Store:
    """Все заметки в памяти + атомарная запись на диск."""

    def __init__(self, path=None):
        self.path = path or DATA_FILE
        self.days = {}
        self.recurring = []
        self.load()

    def load(self):
        raw = {}
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
            except Exception as e:
                # файл повреждён: откладываем его копию, чтобы ничего не потерять
                print("Load error:", self.path, e)
                try:
                    shutil.copy2(self.path, self.path + ".broken-"
                                 + time.strftime("%Y%m%d-%H%M%S"))
                except Exception:
                    pass
        rec = raw.pop("_recurring", []) if isinstance(raw, dict) else []
        self.recurring = [t for t in map(normalize_template, rec if isinstance(rec, list)
                                         else []) if t]
        self.days = normalize_data(raw, pydate.today().isoformat())

    def save(self):
        out = {k: v for k, v in self.days.items()
               if v.get("active") or v.get("archived")}
        if self.recurring:
            out["_recurring"] = self.recurring
        return save_json_atomic(self.path, out)

    # --- повторяющиеся заметки ---
    def template(self, rid):
        return next((t for t in self.recurring if t.get("id") == rid), None)

    def set_rule(self, note, day_key, rule):
        """Создаёт или обновляет шаблон повтора по заметке. Возвращает его id."""
        rule = normalize_rule(rule)
        if rule is None:
            return None
        rid = note.get("rid")
        t = self.template(rid) if rid else None
        remind = note.get("remind") if isinstance(note.get("remind"), dict) else None
        fields = {
            "text": note.get("text", ""), "ci": note.get("ci", 0),
            "w": note.get("w", NOTE_W), "h": note.get("h", NOTE_H), "rule": rule,
            "times": list(remind.get("times") or []) if remind else [],
        }
        if t is None:
            t = {"id": "r-" + str(uuid.uuid4()), "start": day_key, "skip": []}
            self.recurring.append(t)
        else:
            t["start"] = min(t.get("start", day_key), day_key)
            t["skip"] = [k for k in t.get("skip", []) if k != day_key]
        t.update(fields)
        return t["id"]

    def remove_rule(self, rid):
        self.recurring = [t for t in self.recurring if t.get("id") != rid]

    def skip(self, rid, day_key):
        t = self.template(rid)
        if t is not None and day_key not in t["skip"]:
            t["skip"].append(day_key)
            t["skip"] = t["skip"][-200:]

    def materialize(self, day_key, today_key, avail_w):
        """Кладёт на день повторяющиеся заметки, которых там ещё нет (только
        сегодня и в будущем — прошлые дни не заполняются задним числом)."""
        day = parse_key(day_key)
        if day is None or day_key < today_key:
            return 0
        bucket = self.day(day_key)
        have = {n.get("rid") for n in bucket["active"] + bucket["archived"] if n.get("rid")}
        added = 0
        for t in self.recurring:
            if (t["id"] in have or day_key < t["start"] or day_key in t["skip"]
                    or not rule_matches(t["rule"], day)):
                continue
            w, h = t.get("w", NOTE_W), t.get("h", NOTE_H)
            x, y = find_free_spot(rects_of(bucket["active"]), w, h, avail_w)
            note = {"id": str(uuid.uuid4()), "rid": t["id"], "x": x, "y": y, "w": w, "h": h,
                    "text": t.get("text", ""), "ci": t.get("ci", 0),
                    "color": PALETTES["pastel"]["colors"][t.get("ci", 0) % 7],
                    "created": f"{day_key}T00:00:00"}
            if t.get("times"):
                note["remind"] = {"mode": "twice" if len(t["times"]) > 1 else "once",
                                  "times": list(t["times"]), "since": f"{day_key}T00:00:00"}
            bucket["active"].append(note)
            added += 1
        return added

    def day(self, key):
        d = self.days.get(key)
        if d is None:
            d = {"active": [], "archived": []}
            self.days[key] = d
        return d

    def peek(self, key):
        return self.days.get(key) or {"active": [], "archived": []}

    def counts(self, key):
        d = self.days.get(key)
        if not d:
            return 0, 0
        return len(d.get("active") or []), len(d.get("archived") or [])

    def keys_with_active(self):
        keys = [k for k, v in self.days.items()
                if v.get("active") and parse_key(k)]
        return sorted(keys)

    def overdue_keys(self, today_key):
        return [k for k in self.keys_with_active() if k < today_key]

    def carry_overdue(self, today_key, avail_w):
        """Переносит незавершённое из прошлых дней на сегодня."""
        today = self.day(today_key)
        moved = 0
        for key in self.overdue_keys(today_key):
            notes = self.days[key]["active"]
            self.days[key]["active"] = []
            for note in notes:
                if note.get("kind") == "plan":
                    # прошлая «заполнить заметки на завтра» уже не актуальна
                    note["done_at"] = datetime.now().isoformat(timespec="seconds")
                    self.days[key]["archived"].append(note)
                    continue
                t = self.template(note.get("rid")) if note.get("rid") else None
                if t is not None and rule_matches(t["rule"], parse_key(today_key)) \
                        and today_key >= t["start"]:
                    continue  # сегодня у повторяющейся заметки и так свой экземпляр
                note.pop("rid", None)
                note.pop("fired", None)
                note["x"], note["y"] = find_free_spot(
                    rects_of(today["active"]), note.get("w", NOTE_W),
                    note.get("h", NOTE_H), avail_w)
                today["active"].append(note)
                moved += 1
        return moved

    def import_events(self, key, events, avail_w):
        """Добавляет события календаря как заметки, пропуская уже известные."""
        day = self.day(key)
        known = {n.get("yandex_uid") for n in day["active"] + day["archived"]
                 if n.get("source") == "yandex"}
        added = 0
        for ev in sorted(events, key=lambda e: e.get("text", "")):
            uid = ev.get("uid")
            if not uid or uid in known:
                continue
            x, y = find_free_spot(rects_of(day["active"]), NOTE_W, NOTE_H, avail_w)
            day["active"].append({
                "id": str(uuid.uuid4()), "x": x, "y": y,
                "w": NOTE_W, "h": NOTE_H, "text": ev.get("text", ""),
                "ci": YANDEX_CI, "color": PALETTES["pastel"]["colors"][YANDEX_CI],
                "source": "yandex", "yandex_uid": uid,
                "created": datetime.now().isoformat(timespec="seconds"),
            })
            known.add(uid)
            added += 1
        return added

    def add_plan_note(self, key, text, plan_time, avail_w):
        day = self.day(key)
        x, y = find_free_spot(rects_of(day["active"]), NOTE_W, NOTE_H, avail_w)
        note = {
            "id": str(uuid.uuid4()), "x": x, "y": y, "w": NOTE_W, "h": NOTE_H,
            "text": text, "ci": PLAN_CI, "color": PALETTES["pastel"]["colors"][PLAN_CI],
            "kind": "plan", "created": datetime.now().isoformat(timespec="seconds"),
            "remind": {"mode": "once", "times": [plan_time],
                       "since": f"{key}T00:00:00"},
        }
        day["active"].append(note)
        return note

    def search(self, query, limit=60):
        q = (query or "").strip().lower()
        if not q:
            return []
        hits = []
        for key in sorted(self.days, reverse=True):
            if not parse_key(key):
                continue
            day = self.days[key]
            for archived, items in ((False, day.get("active") or []),
                                    (True, day.get("archived") or [])):
                for note in items:
                    text = note.get("text") or ""
                    if q in text.lower():
                        hits.append({"key": key, "archived": archived,
                                     "id": note.get("id"), "text": text})
                        if len(hits) >= limit:
                            return hits
        return hits


# ------------------------- Яндекс.Календарь -----------------------------
def _is_proxy_error(exc):
    text = (exc.__class__.__name__ + " " + str(exc)).lower()
    return "proxy" in text


def _make_dav_client(username, password, direct):
    import caldav
    client = caldav.DAVClient(
        url=YANDEX_URL,
        username=username,
        password=password,
        rate_limit_default_sleep=5,
        rate_limit_max_sleep=30,
    )
    if direct:
        # системный прокси Windows не отвечает — идём к Яндексу напрямую
        session = getattr(client, "session", None)
        if session is not None:
            try:
                session.trust_env = False
            except Exception:
                pass
            try:
                session.proxies = {}
            except Exception:
                pass
    return client


def fetch_yandex_events(username, password, day):
    """Загружает события из Яндекс.Календаря на указанную дату."""
    try:
        return _fetch_events(username, password, day, direct=False)
    except Exception as e:
        if not _is_proxy_error(e):
            raise
        print("Proxy problem, retrying without system proxy:", e)
        os.environ["NO_PROXY"] = ",".join(
            p for p in (os.environ.get("NO_PROXY", ""), "caldav.yandex.ru") if p)
        return _fetch_events(username, password, day, direct=True)


def _fetch_events(username, password, day, direct):
    client = _make_dav_client(username, password, direct)
    principal = client.principal()
    time.sleep(1.5)

    calendars = principal.calendars()
    if not calendars:
        return []

    # Берём первый календарь (обычно «Мои события»)
    my_cal = calendars[0]
    time.sleep(1.5)

    start = datetime.combine(day, datetime.min.time())
    end = start + timedelta(days=1)
    events = my_cal.search(start=start, end=end, event=True, expand=True)

    result = []
    for ev in events:
        parsed = parse_ical_event(ev)
        if parsed:
            result.append(parsed)
    return result


def parse_ical_event(ev):
    """Достаёт из события UID, время и текст."""
    try:
        try:
            cal = ev.icalendar_instance  # новый caldav
        except AttributeError:
            import icalendar
            data = ev.data
            if isinstance(data, bytes):
                data = data.decode("utf-8", errors="replace")
            cal = icalendar.Calendar.from_ical(data)

        for comp in cal.walk("vevent"):
            uid = str(comp.get("UID", "")).strip()
            summary = str(comp.get("SUMMARY", "")).strip()
            description = str(comp.get("DESCRIPTION", "")).strip()

            time_str = ""
            dtstart = comp.get("DTSTART")
            if dtstart is not None:
                dt = dtstart.dt
                if hasattr(dt, "hour"):
                    # время с часовым поясом показываем по местному времени
                    if getattr(dt, "tzinfo", None) is not None:
                        dt = dt.astimezone()
                    time_str = dt.strftime("%H:%M")

            text = summary or T("no_title")
            if time_str:
                text = f"{time_str}  {text}"
            if description:
                text += f"\n{description}"

            return {"uid": uid, "text": text}
    except Exception as e:
        print("Parse error:", e)
    return None


# ----------------------- ярлык и автозапуск ----------------------------
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_NAME = "StickiesNotes"
IS_WIN = sys.platform == "win32"
IS_MAC = sys.platform == "darwin"
IS_LINUX = sys.platform.startswith("linux")
LINUX_AUTOSTART = os.path.join(HOME, ".config", "autostart", "notes-paper.desktop")
MAC_AGENT = os.path.join(HOME, "Library", "LaunchAgents", "app.notes.paper.plist")


def pythonw_path():
    """Интерпретатор без чёрного окна консоли (в Windows — pythonw.exe)."""
    exe = sys.executable or "python3"
    if not IS_WIN:
        return exe
    candidate = os.path.join(os.path.dirname(exe), "pythonw.exe")
    return candidate if os.path.exists(candidate) else exe


def launch_argv(*extra):
    """Команда запуска списком — для автозапуска в Linux и macOS."""
    if FROZEN:
        return [sys.executable, *extra]
    return [pythonw_path(), os.path.abspath(__file__), *extra]


def _png_icon():
    for root in (APP_DIR, getattr(sys, "_MEIPASS", APP_DIR)):
        path = os.path.join(root, "notes.png")
        if os.path.exists(path):
            return path
    return ICON_FILE


def _desktop_entry(extra=""):
    def q(a):
        return '"' + a.replace('"', '\\"') + '"' if " " in a else a
    cmd = " ".join(q(a) for a in launch_argv()) + (f" {extra}" if extra else "")
    return ("[Desktop Entry]\nType=Application\nVersion=1.0\n"
            f"Name={T('app')}\nComment={T('shortcut_desc')}\n"
            f"Exec={cmd}\nIcon={_png_icon()}\nTerminal=false\n"
            "Categories=Office;Utility;\nStartupWMClass=Stickies\n")


def _xdg_desktop():
    try:
        out = subprocess.run(["xdg-user-dir", "DESKTOP"], capture_output=True,
                             text=True, timeout=5).stdout.strip()
        if out and os.path.isdir(out):
            return out
    except Exception:
        pass
    return os.path.join(HOME, "Desktop")


def launch_command():
    """(программа, аргументы) для ярлыка и автозапуска."""
    if FROZEN:
        return sys.executable, ""
    return pythonw_path(), f'"{os.path.abspath(__file__)}"'


def desktop_dir():
    try:
        import ctypes
        buf = ctypes.create_unicode_buffer(520)
        if ctypes.windll.shell32.SHGetFolderPathW(None, 0x10, None, 0, buf) == 0 \
                and buf.value:
            return buf.value
    except Exception:
        pass
    return os.path.join(HOME, "Desktop")


def create_desktop_shortcut():
    """Создаёт ярлык на рабочем столе. Возвращает (успех, текст)."""
    if IS_LINUX:
        return _linux_shortcut()
    if not IS_WIN:
        return False, T("shortcut_only_win")
    name = T("app")
    lnk = os.path.join(desktop_dir(), name + ".lnk")
    target, args = launch_command()

    def q(s):
        return "'" + str(s).replace("'", "''") + "'"

    ps = (
        "$s = (New-Object -ComObject WScript.Shell).CreateShortcut(" + q(lnk) + ");"
        "$s.TargetPath = " + q(target) + ";"
        "$s.Arguments = " + q(args) + ";"
        "$s.WorkingDirectory = " + q(APP_DIR) + ";"
        "$s.Description = " + q(T("shortcut_desc")) + ";"
    )
    icon = ICON_FILE if os.path.exists(ICON_FILE) else (sys.executable if FROZEN else "")
    if icon:
        ps += "$s.IconLocation = " + q(icon + ",0") + ";"
    ps += "$s.Save()"
    encoded = base64.b64encode(ps.encode("utf-16-le")).decode("ascii")
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy",
             "Bypass", "-EncodedCommand", encoded],
            capture_output=True, timeout=40, creationflags=0x08000000)
    except Exception as e:
        return False, T("shortcut_fail") + f"\n{e}"
    if proc.returncode == 0 and os.path.exists(lnk):
        return True, T("shortcut_ok", name=name)
    return False, T("shortcut_fail")


def _linux_shortcut():
    name = T("app")
    entry = _desktop_entry()
    apps = os.path.join(HOME, ".local", "share", "applications")
    try:
        os.makedirs(apps, exist_ok=True)
        targets = [os.path.join(apps, "notes-paper.desktop")]
        desk = _xdg_desktop()
        if os.path.isdir(desk):
            targets.append(os.path.join(desk, "notes-paper.desktop"))
        for path in targets:
            with open(path, "w", encoding="utf-8") as f:
                f.write(entry)
            os.chmod(path, 0o755)
            try:  # GNOME: разрешить запуск ярлыка с рабочего стола
                subprocess.run(["gio", "set", path, "metadata::trusted", "true"],
                               capture_output=True, timeout=5)
            except Exception:
                pass
    except Exception as e:
        return False, T("shortcut_fail") + f"\n{e}"
    return True, T("shortcut_ok_linux", name=name)


def autostart_enabled():
    if IS_LINUX:
        return os.path.exists(LINUX_AUTOSTART)
    if IS_MAC:
        return os.path.exists(MAC_AGENT)
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as k:
            winreg.QueryValueEx(k, RUN_NAME)
        return True
    except Exception:
        return False


def set_autostart(enabled):
    if IS_LINUX or IS_MAC:
        path = LINUX_AUTOSTART if IS_LINUX else MAC_AGENT
        if not enabled:
            if os.path.exists(path):
                os.remove(path)
            return
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if IS_LINUX:
            text = _desktop_entry("--tray") + "X-GNOME-Autostart-enabled=true\n"
        else:
            from xml.sax.saxutils import escape
            args = "".join(f"<string>{escape(a)}</string>" for a in launch_argv("--tray"))
            text = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                    '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" '
                    '"http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
                    '<plist version="1.0"><dict>'
                    '<key>Label</key><string>app.notes.paper</string>'
                    f'<key>ProgramArguments</key><array>{args}</array>'
                    '<key>RunAtLoad</key><true/></dict></plist>\n')
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0,
                        winreg.KEY_SET_VALUE) as k:
        if enabled:
            target, args = launch_command()
            cmd = " ".join(p for p in (f'"{target}"', args, "--tray") if p)
            winreg.SetValueEx(k, RUN_NAME, 0, winreg.REG_SZ, cmd)
        else:
            try:
                winreg.DeleteValue(k, RUN_NAME)
            except FileNotFoundError:
                pass


def setup_logging():
    """Под pythonw нет консоли — пишем ошибки в stickies.log рядом с программой."""
    if sys.stderr is not None and sys.stdout is not None:
        return
    for path in (LOG_FILE, os.path.join(HOME, ".stickies.log")):
        try:
            if os.path.exists(path) and os.path.getsize(path) > 400_000:
                os.replace(path, path + ".old")
            f = open(path, "a", encoding="utf-8", buffering=1)
        except Exception:
            continue
        if sys.stderr is None:
            sys.stderr = f
        if sys.stdout is None:
            sys.stdout = f
        return


def fatal(message) -> NoReturn:
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(None, message, T("app"), 0x10)
    except Exception:
        print(message, file=sys.stderr)
    sys.exit(1)


# ============================== ИНТЕРФЕЙС ===============================
setup_logging()
try:
    from PySide6.QtCore import (
        Qt, QPoint, QPointF, QRect, QRectF, QSize, QTimer, QDate, QTime, QThread,
        Signal, QObject, QEvent, QLocale, QByteArray, QPropertyAnimation,
        QEasingCurve, qInstallMessageHandler
    )
    from PySide6.QtGui import (
        QColor, QFont, QFontMetrics, QFontDatabase, QIcon, QKeySequence, QPainter,
        QPainterPath, QPalette, QPen, QPixmap, QPolygonF, QShortcut, QStandardItemModel,
        QTextCharFormat, QGuiApplication
    )
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QTextEdit, QToolButton,
        QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QLabel, QMenu, QScrollArea,
        QPushButton, QSystemTrayIcon, QCalendarWidget, QDialog, QLineEdit,
        QFormLayout, QMessageBox, QListWidget, QListWidgetItem, QCheckBox,
        QSizePolicy, QTableView, QComboBox, QFontComboBox, QSpinBox, QTimeEdit,
        QRadioButton, QButtonGroup, QListView
    )
    from PySide6.QtNetwork import QLocalServer, QLocalSocket
except ImportError as exc:
    fatal(T("no_pyside") + "\n\n" + str(exc))


# ------------------------------- Тема -----------------------------------
THEMES = {
    "light": {
        "kraft": "#B39A79", "paper": "#F3ECDE", "surface": "#FBF7EF",
        "line": "#D9CDB8", "ink": "#3A2D22", "muted": "#7E6C59",
        "faint": "#B4A58F", "accent": "#74503A", "accent_hover": "#5F402C",
        "on_accent": "#F8F1E4", "hover": "#E9DFCC", "pressed": "#DED1BA",
        "board_ink": "#3E3022", "board_muted": "#5E4B37", "shadow": "#2A1C10",
        "rust": "#9A4A2E",
    },
    "dark": {
        "kraft": "#3B3129", "paper": "#221E1A", "surface": "#2E2924",
        "line": "#3B342D", "ink": "#EDE3D1", "muted": "#A8998A",
        "faint": "#6A5E51", "accent": "#D9A877", "accent_hover": "#E5BA8E",
        "on_accent": "#25211D", "hover": "#322C26", "pressed": "#3B342D",
        "board_ink": "#D8CBB6", "board_muted": "#A8998A", "shadow": "#000000",
        "rust": "#D98A6A",
    },
}
NOTE_INK = "#33281E"
# Шрифты перечислены по предпочтению: Windows, затем встроенные в сборку
# (папка fonts: Caveat, Marck Script, Lora, PT Sans, PT Serif), затем macOS и Linux.
SCRIPT_FONTS = ["Segoe Script", "Segoe Print", "Caveat", "Marck Script", "Ink Free",
                "Gabriola", "Georgia", "Lora", "PT Serif", "DejaVu Serif"]
SERIF_FONTS = ["Georgia", "Lora", "Cambria", "Constantia", "PT Serif", "Charter",
               "Palatino", "Noto Serif", "DejaVu Serif", "Liberation Serif",
               "Times New Roman"]
NOTE_FONTS = ["Segoe Print", "Caveat", "Marck Script", "Georgia", "PT Serif",
              "Noto Serif", "DejaVu Serif"]
UI_FONTS = ["Segoe UI", "PT Sans", "Helvetica Neue", "Ubuntu", "Cantarell",
            "Noto Sans", "DejaVu Sans"]
# Проверенные шрифты для стикеров (в списке остаются только установленные
# и умеющие кириллицу)
FONT_GROUPS = [
    ("font_g_hand", ["Segoe Print", "Segoe Script", "Caveat", "Marck Script", "Ink Free",
                     "Gabriola"]),
    ("font_g_serif", ["Georgia", "Lora", "PT Serif", "Cambria", "Constantia",
                      "Palatino Linotype", "Palatino", "Charter", "Baskerville",
                      "Noto Serif", "DejaVu Serif", "Liberation Serif"]),
    ("font_g_sans", ["Segoe UI", "PT Sans", "Calibri", "Candara", "Corbel",
                     "Helvetica Neue", "Avenir Next", "Ubuntu", "Noto Sans", "DejaVu Sans"]),
    ("font_g_mono", ["Consolas", "Cascadia Mono", "Menlo", "SF Mono", "Ubuntu Mono",
                     "DejaVu Sans Mono", "Liberation Mono"]),
]
OTHER_FONT = "__other__"


class Theme:
    name = "light"
    colors = dict(THEMES["light"])

    @classmethod
    def use(cls, name):
        cls.name = name if name in THEMES else "light"
        cls.colors = dict(THEMES[cls.name])


def C(key):
    return QColor(Theme.colors[key])


_FAMILIES = None


def load_bundled_fonts():
    """Подключает шрифты из папки fonts рядом с программой (или внутри сборки)."""
    global _FAMILIES
    added = []
    for root in {APP_DIR, getattr(sys, "_MEIPASS", APP_DIR)}:
        folder = os.path.join(root, "fonts")
        if not os.path.isdir(folder):
            continue
        for name in sorted(os.listdir(folder)):
            if name.lower().endswith((".ttf", ".otf")):
                fid = QFontDatabase.addApplicationFont(os.path.join(folder, name))
                if fid >= 0:
                    added += QFontDatabase.applicationFontFamilies(fid)
    _FAMILIES = None
    return sorted(set(added))


def pick_family(candidates, cyrillic=True):
    """Первый установленный шрифт из списка (по умолчанию — с кириллицей)."""
    global _FAMILIES
    if _FAMILIES is None:
        try:
            _FAMILIES = set(QFontDatabase.families())
        except Exception:
            _FAMILIES = set()
    for fam in candidates:
        if fam in _FAMILIES and (not cyrillic or font_supports_cyrillic(fam)):
            return fam
    for fam in candidates:
        if fam in _FAMILIES:
            return fam
    return candidates[-1]


def ui_family():
    fam = pick_family(UI_FONTS)
    if fam in (_FAMILIES or set()):
        return fam
    try:
        return QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont).family()
    except Exception:
        return fam


def font_supports_cyrillic(family):
    try:
        return QFontDatabase.WritingSystem.Cyrillic in QFontDatabase.writingSystems(family)
    except Exception:
        return True


def curated_fonts():
    """[(ключ группы, [семейства])] — только установленные шрифты с кириллицей."""
    pick_family(["Georgia"])  # заполняет кэш семейств
    out = []
    for key, fams in FONT_GROUPS:
        ok = [f for f in fams if (not _FAMILIES or f in _FAMILIES) and font_supports_cyrillic(f)]
        if ok:
            out.append((key, ok))
    return out


def script_font(px):
    f = QFont(pick_family(SCRIPT_FONTS))
    f.setPixelSize(px)
    return f


def serif_font(px):
    f = QFont(pick_family(SERIF_FONTS))
    f.setPixelSize(px)
    return f


def spaced_font(pixel_size=10, spacing=1.3):
    f = QFont(ui_family())
    f.setPixelSize(pixel_size)
    f.setBold(True)
    f.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, spacing)
    return f


QSS = Template("""
QWidget#Root { background: $kraft; }
QDialog, QMessageBox { background: $paper; }

QLabel { color: $ink; background: transparent; }
QLabel#MonthLabel { font-size: 14px; font-weight: 600; }
QLabel#Weekday { color: $accent; }
QLabel#Section, QLabel#Stats, QLabel#Status, QLabel#Hint, QLabel#Count { color: $muted; }
QLabel#CountHot { color: $rust; font-weight: 600; }

QLineEdit, QTimeEdit, QSpinBox, QComboBox {
    background: $surface; color: $ink; border: 1px solid $line;
    border-radius: 7px; padding: 6px 9px;
    selection-background-color: $accent; selection-color: $on_accent;
}
QTimeEdit, QSpinBox { padding: 4px 8px; }
QLineEdit:focus, QTimeEdit:focus, QSpinBox:focus, QComboBox:focus { border: 1px solid $accent; }
QTimeEdit:disabled { color: $faint; }
QComboBox::drop-down { border: none; width: 22px; }
QComboBox QAbstractItemView {
    background: $surface; color: $ink; border: 1px solid $line;
    selection-background-color: $hover; selection-color: $ink; outline: 0;
}
QTimeEdit::up-button, QTimeEdit::down-button, QSpinBox::up-button, QSpinBox::down-button {
    width: 16px; border: none; background: transparent;
}

QPushButton {
    background: transparent; color: $ink; border: 1px solid $line;
    border-radius: 7px; padding: 7px 14px;
}
QPushButton:hover { background: $hover; }
QPushButton:pressed { background: $pressed; }
QPushButton:checked { background: $hover; border: 1px solid $faint; }
QPushButton:disabled { color: $faint; }
QPushButton#Primary {
    background: $accent; color: $on_accent; border: 1px solid $accent; font-weight: 600;
}
QPushButton#Primary:hover { background: $accent_hover; border: 1px solid $accent_hover; }
QPushButton#Flat { border: none; color: $muted; padding: 6px 8px; text-align: left; }
QPushButton#Flat:hover { color: $ink; background: $hover; }
QPushButton#Nav { padding: 0; font-size: 17px; }
QPushButton#Compact { padding: 0 14px; }
QPushButton#Quick { padding: 5px 11px; border-radius: 13px; }
QPushButton#Day { min-width: 34px; max-width: 34px; min-height: 30px; max-height: 30px;
    padding: 0; border-radius: 15px; }
QPushButton#Day:checked { background: $accent; color: $on_accent; border: 1px solid $accent; }

QCheckBox, QRadioButton { color: $ink; spacing: 8px; background: transparent; }
QRadioButton::indicator { width: 14px; height: 14px; border-radius: 8px;
    border: 1px solid $faint; background: $surface; }
QRadioButton::indicator:checked { border: 5px solid $accent; background: $surface;
    width: 6px; height: 6px; }
QCheckBox::indicator { width: 14px; height: 14px; border-radius: 4px;
    border: 1px solid $faint; background: $surface; }
QCheckBox::indicator:checked { background: $accent; border: 1px solid $accent; }
QCheckBox::indicator:disabled, QRadioButton::indicator:disabled { background: $line; }
QCalendarWidget QAbstractItemView { selection-background-color: transparent;
    selection-color: $ink; background: transparent; outline: 0; }
QAbstractScrollArea::corner { background: transparent; border: none; }

QListWidget { background: transparent; border: none; outline: 0; color: $ink; }
QListWidget::item { border-radius: 7px; }
QListWidget::item:hover { background: $hover; }
QListWidget::item:selected { background: $hover; color: $ink; }

QScrollArea { background: transparent; border: none; }
QScrollArea > QWidget > QWidget { background: transparent; }
QScrollBar:vertical { background: transparent; width: 10px; margin: 2px; }
QScrollBar:horizontal { background: transparent; height: 10px; margin: 2px; }
QScrollBar::handle { background: rgba(90, 70, 50, 90); border-radius: 3px; }
QScrollBar::handle:vertical { min-height: 28px; }
QScrollBar::handle:horizontal { min-width: 28px; }
QScrollBar::handle:hover { background: rgba(90, 70, 50, 150); }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }

QMenu { background: $surface; color: $ink; border: 1px solid $line; padding: 5px; }
QMenu::item { padding: 6px 24px 6px 12px; border-radius: 5px; }
QMenu::item:selected { background: $hover; color: $ink; }
QMenu::separator { height: 1px; background: $line; margin: 5px 8px; }
QToolTip { background: $ink; color: $paper; border: none; padding: 4px 8px; }
""")


def build_palette():
    pal = QPalette()
    ink, bg = C("ink"), C("paper")
    pal.setColor(QPalette.ColorRole.Window, bg)
    pal.setColor(QPalette.ColorRole.WindowText, ink)
    pal.setColor(QPalette.ColorRole.Base, C("surface"))
    pal.setColor(QPalette.ColorRole.AlternateBase, C("paper"))
    pal.setColor(QPalette.ColorRole.Text, ink)
    pal.setColor(QPalette.ColorRole.Button, C("surface"))
    pal.setColor(QPalette.ColorRole.ButtonText, ink)
    pal.setColor(QPalette.ColorRole.Highlight, C("accent"))
    pal.setColor(QPalette.ColorRole.HighlightedText, C("on_accent"))
    pal.setColor(QPalette.ColorRole.ToolTipBase, ink)
    pal.setColor(QPalette.ColorRole.ToolTipText, bg)
    pal.setColor(QPalette.ColorRole.PlaceholderText, C("muted"))
    pal.setColor(QPalette.ColorRole.Link, C("accent"))
    for role in (QPalette.ColorRole.WindowText, QPalette.ColorRole.Text,
                 QPalette.ColorRole.ButtonText):
        pal.setColor(QPalette.ColorGroup.Disabled, role, C("faint"))
    return pal


# ----------------------------- Текстуры ---------------------------------
_TEX = {}


def _make_texture(key, base, size, density, dark, light, fibers, seed):
    """Плитка бумажной текстуры: мелкое зерно, вкрапления и волокна."""
    if key in _TEX:
        return _TEX[key]
    pm = QPixmap(size, size)
    pm.fill(base if base is not None else QColor(0, 0, 0, 0))
    rnd = random.Random(seed)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
    dr, dg, db = dark
    lr, lg, lb = light
    for _ in range(int(size * size * density)):
        x, y = rnd.randrange(size), rnd.randrange(size)
        if rnd.random() < 0.55:
            p.setPen(QColor(dr, dg, db, rnd.randint(8, 26)))
        else:
            p.setPen(QColor(lr, lg, lb, rnd.randint(10, 34)))
        p.drawPoint(x, y)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    for _ in range(fibers):
        x, y = rnd.uniform(0, size), rnd.uniform(0, size)
        a = rnd.uniform(0, math.pi)
        ln = rnd.uniform(3, 11)
        p.setPen(QPen(QColor(dr, dg, db, rnd.randint(14, 40)), rnd.uniform(0.5, 1.0)))
        p.drawLine(QPointF(x, y), QPointF(x + ln * math.cos(a), y + ln * math.sin(a)))
    # тёмные вкрапления, как в бумаге ручного отлива
    p.setPen(Qt.PenStyle.NoPen)
    for _ in range(max(1, int(size * size / 5200))):
        x, y = rnd.uniform(0, size), rnd.uniform(0, size)
        p.setBrush(QColor(dr, dg, db, rnd.randint(50, 110)))
        r = rnd.uniform(0.5, 1.1)
        p.drawEllipse(QPointF(x, y), r, r)
    p.end()
    _TEX[key] = pm
    return pm


def kraft_texture():
    c = C("kraft")
    if Theme.name == "dark":
        return _make_texture("kraft-dark", c, 220, 0.20, (0, 0, 0), (120, 100, 80),
                             90, 11)
    return _make_texture("kraft-light", c, 220, 0.26, (70, 50, 30), (225, 205, 175),
                         140, 7)


def paper_texture():
    c = C("paper")
    if Theme.name == "dark":
        return _make_texture("paper-dark", c, 220, 0.10, (0, 0, 0), (90, 80, 70),
                             40, 13)
    return _make_texture("paper-light", c, 220, 0.12, (110, 85, 60), (255, 255, 250),
                         60, 5)


def speckle_overlay():
    """Прозрачная плитка с зерном — накладывается поверх цвета стикера."""
    return _make_texture("speckle", None, 200, 0.10, (90, 65, 40), (255, 255, 248),
                         50, 3)


# --------------------------- Рваная бумага ------------------------------
def torn_points(x0, y0, x1, y1, rnd, amp, step, normal):
    """Точки неровного края от (x0,y0) к (x1,y1); отклонения — внутрь листа."""
    length = math.hypot(x1 - x0, y1 - y0)
    n = max(2, int(length / step))
    nx, ny = normal
    phase = rnd.uniform(0, 6.28)
    freq = rnd.uniform(0.6, 1.4) * length / 60.0
    pts = []
    for i in range(n):
        t = i / n
        bx, by = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        off = -amp * (0.5 + 0.5 * math.sin(phase + t * freq * 6.28)) * 0.7
        off -= rnd.uniform(0, amp)
        if rnd.random() < 0.035:
            off -= amp * rnd.uniform(0.8, 1.6)
        pts.append(QPointF(bx + nx * off, by + ny * off))
    return pts


def torn_path(rect, seed, amp=2.4, step=4.5, sides="tlbr"):
    """Контур листа с рваными краями (sides — какие стороны рвать)."""
    rnd = random.Random(seed)
    L, T_, R, B = rect.left(), rect.top(), rect.right(), rect.bottom()
    pts = []

    def side(flag, x0, y0, x1, y1, normal):
        if flag in sides:
            pts.extend(torn_points(x0, y0, x1, y1, rnd, amp, step, normal))
        else:
            pts.append(QPointF(x0, y0))

    side("t", L, T_, R, T_, (0, -1))
    side("r", R, T_, R, B, (1, 0))
    side("b", R, B, L, B, (0, 1))
    side("l", L, B, L, T_, (-1, 0))
    path = QPainterPath()
    path.addPolygon(QPolygonF(pts))
    path.closeSubpath()
    return path


def note_seed(note_id):
    return int(hashlib.md5(str(note_id).encode("utf-8")).hexdigest()[:8], 16)


def draw_tape(p, cx, cy, angle, w=72, h=21, color=None):
    """Полоска бумажного скотча с рваными концами."""
    p.save()
    p.translate(cx, cy)
    p.rotate(angle)
    rnd = random.Random(int(cx * 7 + cy * 13 + angle * 3))
    pts = [QPointF(-w / 2, -h / 2), QPointF(w / 2, -h / 2)]
    for i in range(1, 6):
        pts.append(QPointF(w / 2 + rnd.uniform(-2.5, 1.5), -h / 2 + h * i / 6))
    pts += [QPointF(w / 2, h / 2), QPointF(-w / 2, h / 2)]
    for i in range(5, 0, -1):
        pts.append(QPointF(-w / 2 + rnd.uniform(-1.5, 2.5), -h / 2 + h * i / 6))
    path = QPainterPath()
    path.addPolygon(QPolygonF(pts))
    path.closeSubpath()
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(60, 40, 20, 22))
    p.drawPath(path.translated(0.6, 1.4))
    p.setBrush(color or QColor(238, 229, 209, 200))
    p.drawPath(path)
    p.setPen(QPen(QColor(255, 255, 255, 70), 1))
    p.drawLine(QPointF(-w / 2 + 3, -h / 2 + 3), QPointF(w / 2 - 3, -h / 2 + 3))
    p.restore()


def draw_clip(p, x, y, angle=14.0, scale=1.0):
    """Канцелярская скрепка (как на референсе)."""
    p.save()
    p.translate(x, y)
    p.rotate(angle)
    p.scale(scale, scale)
    path = QPainterPath()
    path.moveTo(9.5, 9)
    path.lineTo(9.5, 33)
    path.arcTo(QRectF(0, 28.5, 9.5, 9.5), 0, -180)
    path.lineTo(0, 6.5)
    path.arcTo(QRectF(0, 0, 13.5, 13.5), 180, -180)
    path.lineTo(13.5, 29)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(QColor(40, 28, 16, 45), 2.6, Qt.PenStyle.SolidLine,
                  Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    p.drawPath(path.translated(1.2, 1.6))
    p.setPen(QPen(QColor("#5E4A36"), 2.2, Qt.PenStyle.SolidLine,
                  Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    p.drawPath(path)
    p.setPen(QPen(QColor(230, 210, 180, 120), 0.7))
    p.drawPath(path.translated(-0.5, -0.5))
    p.restore()


_FLOWERS = {}


def dried_flowers_pixmap(dpr=1.0):
    """Букетик сухоцвета (гипсофила) со скотчем — как на референсе."""
    key = round(dpr, 2)
    if key in _FLOWERS:
        return _FLOWERS[key]
    W, H = 280, 340
    pm = QPixmap(int(W * dpr), int(H * dpr))
    pm.setDevicePixelRatio(dpr)
    pm.fill(Qt.GlobalColor.transparent)
    rnd = random.Random(42)
    base = QPointF(W - 78, H - 26)

    stems, clusters = [], []
    for i in range(5):
        ang = math.radians(-34 + i * 9 + rnd.uniform(-4, 4))
        length = rnd.uniform(200, 260) - abs(i - 2) * 12
        bend = rnd.uniform(-18, 18)
        start = QPointF(base.x() + rnd.uniform(-5, 5), base.y() + rnd.uniform(-4, 4))
        end = QPointF(start.x() + math.sin(ang) * length,
                      start.y() - math.cos(ang) * length)
        c1 = QPointF(start.x() + (end.x() - start.x()) * 0.35 + bend,
                     start.y() + (end.y() - start.y()) * 0.35)
        c2 = QPointF(start.x() + (end.x() - start.x()) * 0.7 + bend * 0.5,
                     start.y() + (end.y() - start.y()) * 0.7)
        path = QPainterPath(start)
        path.cubicTo(c1, c2, end)
        stems.append((path, 1.4))
        clusters.append(end)
        for _ in range(rnd.randint(2, 4)):
            t = rnd.uniform(0.45, 0.9)
            pt = path.pointAtPercent(t)
            a2 = ang + math.radians(rnd.choice((-1, 1)) * rnd.uniform(18, 38))
            ln = rnd.uniform(26, 58)
            tip = QPointF(pt.x() + math.sin(a2) * ln, pt.y() - math.cos(a2) * ln)
            br = QPainterPath(pt)
            br.quadTo(QPointF((pt.x() + tip.x()) / 2 + rnd.uniform(-5, 5),
                              (pt.y() + tip.y()) / 2), tip)
            stems.append((br, 0.9))
            clusters.append(tip)

    flowers, twigs = [], []
    for c in clusters:
        for _ in range(rnd.randint(6, 11)):
            a = rnd.uniform(0, 6.28)
            r = rnd.uniform(3, 15)
            f = QPointF(c.x() + math.cos(a) * r, c.y() + math.sin(a) * r * 0.8 - 3)
            twigs.append((c, f))
            tone = rnd.random()
            flowers.append((f, rnd.uniform(2.1, 3.0), rnd.uniform(0, 6.28),
                            QColor(int(240 - 22 * tone), int(228 - 32 * tone),
                                   int(206 - 48 * tone))))

    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    stem_c, petal_edge, center = (QColor("#8C7150"), QColor(150, 120, 80, 120),
                                  QColor("#9A7448"))

    def draw(shadow):
        dx, dy = (3.0, 5.0) if shadow else (0.0, 0.0)
        sc = QColor(40, 25, 10, 38) if shadow else stem_c
        p.setBrush(Qt.BrushStyle.NoBrush)
        for path, w in stems:
            p.setPen(QPen(sc, w, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawPath(path.translated(dx, dy))
        p.setPen(QPen(sc, 0.6))
        for a, b in twigs:
            p.drawLine(QPointF(a.x() + dx, a.y() + dy), QPointF(b.x() + dx, b.y() + dy))
        for f, r, rot, tint in flowers:
            cx, cy = f.x() + dx, f.y() + dy
            if shadow:
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(QColor(40, 25, 10, 30))
                p.drawEllipse(QPointF(cx, cy), r * 1.9, r * 1.9)
                continue
            p.setPen(QPen(petal_edge, 0.5))
            p.setBrush(tint)
            for k in range(5):
                a = rot + k * 1.2566
                p.drawEllipse(QPointF(cx + math.cos(a) * r * 0.85,
                                      cy + math.sin(a) * r * 0.85), r * 0.72, r * 0.72)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(center)
            p.drawEllipse(QPointF(cx, cy), r * 0.38, r * 0.38)

    draw(True)
    draw(False)
    draw_tape(p, base.x() - 8, base.y() - 42, -12, w=78, h=23)
    p.end()
    _FLOWERS[key] = pm
    return pm


def paint_paper(p, path, color, seed, grid=False):
    """Заливка листа: цвет, зерно, светлая кромка рваного края."""
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(color)
    p.drawPath(path)
    p.save()
    p.setClipPath(path)
    tex = speckle_overlay()
    p.drawTiledPixmap(path.boundingRect().toRect(), tex,
                      QPoint(seed % tex.width(), (seed >> 8) % tex.height()))
    if grid:
        r = path.boundingRect()
        p.setPen(QPen(QColor(120, 105, 85, 34), 1))
        step = 14
        x = r.left() + 6
        while x < r.right():
            p.drawLine(QPointF(x, r.top()), QPointF(x, r.bottom()))
            x += step
        y = r.top() + 6
        while y < r.bottom():
            p.drawLine(QPointF(r.left(), y), QPointF(r.right(), y))
            y += step
    p.restore()
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(QColor(255, 253, 246, 150), 1.6))
    p.drawPath(path)
    p.setPen(QPen(QColor(110, 85, 55, 40), 0.8))
    p.drawPath(path)


def paint_icon_pixmap(size=64):
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    s = size / 64.0
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#F2EADA"))
    p.drawRoundedRect(QRectF(6 * s, 6 * s, 52 * s, 52 * s), 9 * s, 9 * s)
    p.setPen(QPen(QColor(NOTE_INK), 3.4 * s, Qt.PenStyle.SolidLine,
                  Qt.PenCapStyle.RoundCap))
    for y, x2 in ((25, 46), (35, 40), (45, 31)):
        p.drawLine(QPointF(18 * s, y * s), QPointF(x2 * s, y * s))
    p.end()
    return pm


def make_app_icon():
    if os.path.exists(ICON_FILE):
        icon = QIcon(ICON_FILE)
        if not icon.isNull() and icon.availableSizes():
            return icon
    icon = QIcon()
    for size in (16, 24, 32, 48, 64, 128):
        icon.addPixmap(paint_icon_pixmap(size))
    return icon


def swatch_icon(color, size=14):
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(QPen(QColor(0, 0, 0, 60), 1))
    p.setBrush(QColor(color))
    p.drawEllipse(QRectF(1, 1, size - 2, size - 2))
    p.end()
    return QIcon(pm)


def palette_strip_icon(palette, w=84, h=16):
    pm = QPixmap(w, h)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    colors = PALETTES[palette]["colors"]
    cw = w / len(colors)
    for i, c in enumerate(colors):
        p.setPen(QPen(QColor(0, 0, 0, 40), 1))
        p.setBrush(QColor(c))
        p.drawRoundedRect(QRectF(i * cw + 1, 1, cw - 2, h - 2), 3, 3)
    p.end()
    return QIcon(pm)


class PaperPanel(QFrame):
    """Панель-лист кремовой бумаги с одним рваным краем поверх крафта."""

    def __init__(self, edge, name):
        super().__init__()
        self.edge = edge  # "right" | "bottom" | "left"
        self.setObjectName(name)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self._path = None
        self._size = None

    def _paper_path(self):
        size = (self.width(), self.height())
        if self._path is None or self._size != size:
            w, h = size
            seed = {"right": 101, "bottom": 202, "left": 303}[self.edge]
            if self.edge == "right":
                rect, sides = QRectF(-10, -10, w + 4, h + 20), "r"
            elif self.edge == "left":
                rect, sides = QRectF(6, -10, w + 10, h + 20), "l"
            else:
                rect, sides = QRectF(-10, -10, w + 20, h + 4), "b"
            self._path = torn_path(rect, seed, amp=2.8, step=4.0, sides=sides)
            self._size = size
        return self._path

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._path = None

    def paintEvent(self, event):
        p = QPainter(self)
        p.drawTiledPixmap(self.rect(), kraft_texture(),
                          self.mapTo(self.window(), QPoint(0, 0)))
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = self._paper_path()
        shade = C("shadow")
        p.setPen(Qt.PenStyle.NoPen)
        for i, a in ((3, 14), (2, 20), (1, 26)):
            shade.setAlpha(a)
            p.setBrush(shade)
            dx, dy = {"right": (i, 0), "left": (-i, 0), "bottom": (0, i)}[self.edge]
            p.drawPath(path.translated(dx, dy))
        p.save()
        p.setClipPath(path)
        p.drawTiledPixmap(self.rect(), paper_texture())
        p.restore()
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(QColor(255, 255, 250, 120 if Theme.name == "light" else 25), 1.6))
        p.drawPath(path)


# ------------------------------ Стикер ----------------------------------
class IconButton(QToolButton):
    """Маленькая кнопка с нарисованным значком: check / close / more / bell."""

    def __init__(self, kind, tip, note):
        super().__init__(note)
        self.kind = kind
        self.note = note
        self.active = False
        self.setToolTip(tip)
        self.setFixedSize(24, 24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

    def paintEvent(self, event):
        if not self.note.hovered:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        hot = self.underMouse()
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        if hot:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(60, 40, 20, 34 if self.isDown() else 22))
            p.drawEllipse(r)
        ink = QColor(51, 40, 30, 235 if hot else 150)
        c = r.center()
        s = 4.2
        if self.kind == "more":
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(ink)
            for dx in (-5.0, 0.0, 5.0):
                p.drawEllipse(QPointF(c.x() + dx, c.y()), 1.5, 1.5)
            return
        pen = QPen(ink, 1.6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                   Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        if self.kind == "check":
            path = QPainterPath()
            path.moveTo(c.x() - s * 1.15, c.y() + s * 0.05)
            path.lineTo(c.x() - s * 0.3, c.y() + s * 0.9)
            path.lineTo(c.x() + s * 1.2, c.y() - s * 0.85)
            p.drawPath(path)
        elif self.kind == "bell":
            p.setPen(QPen(ink, 1.4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                          Qt.PenJoinStyle.RoundJoin))
            if self.active:
                p.setBrush(QColor(116, 80, 58, 225))
            p.drawPath(bell_path(c.x(), c.y()))
        else:  # close
            p.drawLine(QPointF(c.x() - s, c.y() - s), QPointF(c.x() + s, c.y() + s))
            p.drawLine(QPointF(c.x() - s, c.y() + s), QPointF(c.x() + s, c.y() - s))


def bell_path(cx, cy, s=1.0):
    bell = QPainterPath()
    bell.moveTo(cx - 5 * s, cy + 3.2 * s)
    bell.lineTo(cx - 4 * s, cy + 1.6 * s)
    bell.lineTo(cx - 4 * s, cy - 1.2 * s)
    bell.cubicTo(cx - 4 * s, cy - 5.6 * s, cx + 4 * s, cy - 5.6 * s,
                 cx + 4 * s, cy - 1.2 * s)
    bell.lineTo(cx + 4 * s, cy + 1.6 * s)
    bell.lineTo(cx + 5 * s, cy + 3.2 * s)
    bell.closeSubpath()
    bell.addEllipse(QPointF(cx, cy + 5.0 * s), 1.4 * s, 1.4 * s)
    return bell


class BellTag(QWidget):
    """Колокольчик и время напоминания; по щелчку — настройка напоминания."""

    clicked = Signal()

    def __init__(self, parent=None, color=QColor(116, 80, 58, 230), clickable=True,
                 icon="bell"):
        super().__init__(parent)
        self.text = ""
        self.icon = icon
        self.color = QColor(color)
        f = QFont(ui_family())
        f.setPixelSize(11)
        f.setBold(True)
        self.setFont(f)
        if clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(18)

    def set_text(self, text):
        self.text = text
        self.setFixedWidth(20 + QFontMetrics(self.font()).horizontalAdvance(text) + 4)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.icon == "repeat":
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(self.color, 1.4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawArc(QRectF(2.5, 4, 9, 9), 60 * 16, 280 * 16)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(self.color)
            arrow = QPainterPath()
            arrow.moveTo(9.6, 2.2)
            arrow.lineTo(12.4, 6.0)
            arrow.lineTo(7.8, 6.4)
            arrow.closeSubpath()
            p.drawPath(arrow)
        else:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(self.color)
            p.drawPath(bell_path(7, 8.5, 0.95))
        p.setPen(self.color)
        p.drawText(QRectF(18, 0, self.width() - 18, self.height()),
                   int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft), self.text)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        e.accept()

    def mousePressEvent(self, e):
        e.accept()


class ResizeGrip(QWidget):
    """Уголок, за который тянут, чтобы изменить размер стикера."""

    def __init__(self, note):
        super().__init__(note)
        self.note = note
        self._start = None
        self._size = None
        self.setFixedSize(16, 16)
        self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        self.setToolTip(T("grip"))

    def paintEvent(self, event):
        if not self.note.hovered:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QPen(QColor(51, 40, 30, 90), 1.3, Qt.PenStyle.SolidLine,
                      Qt.PenCapStyle.RoundCap))
        w, h = self.width(), self.height()
        p.drawLine(QPointF(w - 4, h - 12), QPointF(w - 12, h - 4))
        p.drawLine(QPointF(w - 4, h - 7), QPointF(w - 7, h - 4))

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._start = e.globalPosition().toPoint()
            self._size = self.note.size()
            self.note.board.raise_note(self.note)
            e.accept()

    def mouseMoveEvent(self, e):
        if self._start is not None and self._size is not None:
            d = e.globalPosition().toPoint() - self._start
            self.note.resize(max(NOTE_MIN_W, self._size.width() + d.x()),
                             max(NOTE_MIN_H, self._size.height() + d.y()))
            e.accept()

    def mouseReleaseEvent(self, e):
        if self._start is not None:
            self._start = None
            self.note.board.note_geometry_changed()
            e.accept()


class NoteWidget(QFrame):
    KNOWN = ("id", "x", "y", "w", "h", "text", "color", "ci", "source",
             "yandex_uid", "remind", "fired", "created", "kind", "rid")

    def __init__(self, board, data):
        super().__init__(board)
        self.board = board
        ctl = board.ctl
        self.note_id = str(data.get("id") or uuid.uuid4())
        self.seed = note_seed(self.note_id)
        ci = data.get("ci")
        self.ci = ci if isinstance(ci, int) else color_index(data.get("color"))
        self.source = data.get("source", "local")
        self.yandex_uid = data.get("yandex_uid")
        self.kind = data.get("kind")
        self.rid = data.get("rid")
        self.created = data.get("created") or datetime.now().isoformat(timespec="seconds")
        self.remind = data.get("remind") if isinstance(data.get("remind"), dict) else None
        self.fired = list(data.get("fired") or [])
        self.extra = {k: v for k, v in data.items() if k not in self.KNOWN}
        self.hovered = False
        self._drag = None
        self._path = None
        self._path_size = None
        # 0 — скотч по центру, 1 — скотч наискосок, 2 — скрепка
        self.deco = 2 if self.kind == "plan" else self.seed % 3

        self.setObjectName("Note")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setMinimumSize(NOTE_MIN_W, NOTE_MIN_H)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(
            lambda pos: self.show_menu(self.mapToGlobal(pos)))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(PAPER_L + 13, PAPER_T + 9, PAPER_R + 7, PAPER_B + 9)
        layout.setSpacing(2)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(0)
        tag_text, tag_tip, tag_color = None, None, None
        if self.kind == "plan":
            tag_text, tag_tip, tag_color = T("tag_plan"), T("tag_plan_tip"), "154,74,46"
        elif self.source == "yandex":
            tag_text, tag_tip, tag_color = T("tag_yandex"), T("tag_yandex_tip"), "51,40,30"
        if self.deco == 2:
            top.addSpacing(20)
        if tag_text:
            tag = QLabel(tag_text)
            tag.setFont(spaced_font(9, 1.1))
            tag.setToolTip(tag_tip or "")
            tag.setStyleSheet(
                f"QLabel {{ color: rgba({tag_color},215); background: rgba(255,255,255,110);"
                f" border: 1px solid rgba({tag_color},90); border-radius: 3px;"
                " padding: 1px 6px; }")
            top.addWidget(tag)
        top.addStretch(1)

        self.bell_btn = IconButton("bell", T("btn_bell"), self)
        self.bell_btn.clicked.connect(lambda *_: ctl.edit_reminder(self))
        self.more_btn = IconButton("more", T("btn_more"), self)
        self.more_btn.clicked.connect(lambda *_: self.show_menu(
            self.more_btn.mapToGlobal(QPoint(0, self.more_btn.height()))))
        self.done_btn = IconButton("check", T("btn_done"), self)
        self.done_btn.clicked.connect(lambda *_: ctl.complete_note(self))
        top.addWidget(self.bell_btn)
        top.addWidget(self.more_btn)
        top.addWidget(self.done_btn)
        self.del_btn = None
        if self.kind != "plan":
            self.del_btn = IconButton("close", T("btn_delete"), self)
            self.del_btn.clicked.connect(lambda *_: ctl.delete_note(self))
            top.addWidget(self.del_btn)
        layout.addLayout(top)

        self.edit = QTextEdit()
        self.edit.setAcceptRichText(False)
        self.edit.setFrameShape(QFrame.Shape.NoFrame)
        self.edit.setPlaceholderText(T("placeholder"))
        self.edit.setStyleSheet(
            "QTextEdit { background: transparent; border: none; color: #33281E;"
            " selection-background-color: rgba(51,40,30,55); selection-color: #33281E; }")
        pal = self.edit.palette()
        pal.setColor(QPalette.ColorRole.PlaceholderText, QColor(51, 40, 30, 105))
        pal.setColor(QPalette.ColorRole.Text, QColor(NOTE_INK))
        self.edit.setPalette(pal)
        self.edit.setPlainText(data.get("text") or "")
        self.edit.textChanged.connect(self.board.note_changed)
        self.edit.installEventFilter(self)
        layout.addWidget(self.edit, 1)

        bottom = QHBoxLayout()
        bottom.setContentsMargins(0, 0, 0, 0)
        bottom.setSpacing(10)
        self.rem_label = BellTag(self)
        self.rem_label.setToolTip(T("btn_bell"))
        self.rem_label.clicked.connect(lambda: ctl.edit_reminder(self))
        self.rep_label = BellTag(self, icon="repeat")
        self.rep_label.setToolTip(T("btn_repeat"))
        self.rep_label.clicked.connect(lambda: ctl.edit_repeat(self))
        bottom.addWidget(self.rem_label)
        bottom.addWidget(self.rep_label)
        bottom.addStretch(1)
        layout.addLayout(bottom)

        self.grip = ResizeGrip(self)
        self.apply_font()
        self.update_reminder_view()
        self.resize(max(NOTE_MIN_W, _to_int(data.get("w"), NOTE_W)),
                    max(NOTE_MIN_H, _to_int(data.get("h"), NOTE_H)))
        self.move(max(0, _to_int(data.get("x"), 28)),
                  max(0, _to_int(data.get("y"), 28)))
        self._place_grip()

    # --- вид ---
    @property
    def color(self):
        return palette_color(self.board.ctl.sticker_palette(), self.ci)

    def apply_font(self):
        fam, size = self.board.ctl.note_font()
        f = QFont(fam)
        f.setPixelSize(size)
        self.edit.setFont(f)
        self.edit.document().setDefaultFont(f)

    def update_reminder_view(self):
        active = bool(self.remind and self.remind.get("times"))
        self.bell_btn.active = active
        self.bell_btn.update()
        if active and self.remind:
            parts = list(self.remind.get("times") or [])
            snooze = parse_dt(self.remind.get("snooze"))
            if snooze:
                parts.append(snooze.strftime("%H:%M"))
            self.rem_label.set_text("  ·  ".join(parts))
            self.rem_label.show()
        else:
            self.rem_label.hide()
        t = self.board.ctl.store.template(self.rid) if self.rid else None
        if t is not None:
            self.rep_label.set_text(rule_text(t["rule"]))
            self.rep_label.show()
        else:
            self.rep_label.hide()

    def paper_rect(self):
        return QRectF(PAPER_L, PAPER_T, self.width() - PAPER_L - PAPER_R,
                      self.height() - PAPER_T - PAPER_B)

    def paper_path(self):
        size = (self.width(), self.height())
        if self._path is None or self._path_size != size:
            self._path = torn_path(self.paper_rect(), self.seed)
            self._path_size = size
        return self._path

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        grid = PALETTES.get(self.board.ctl.sticker_palette(), {}).get("grid") == self.ci
        paint_paper(p, self.paper_path(), QColor(self.color), self.seed, grid)
        w = self.width()
        if self.deco == 0:
            draw_tape(p, w * 0.40, PAPER_T + 1, (self.seed % 7) - 6)
        elif self.deco == 1:
            draw_tape(p, 30, PAPER_T + 8, -38 + (self.seed % 9), w=62, h=19)
        else:
            draw_clip(p, 16, -1, 10 + (self.seed % 8))

    def _place_grip(self):
        grip = getattr(self, "grip", None)
        if grip is not None:
            grip.move(self.width() - grip.width() - PAPER_R - 2,
                      self.height() - grip.height() - PAPER_B - 2)
            grip.raise_()

    def _set_hover(self, on):
        if self.hovered != on:
            self.hovered = on
            for b in (self.bell_btn, self.more_btn, self.done_btn, self.del_btn, self.grip):
                if b is not None:
                    b.update()

    def event(self, e):
        if e.type() == QEvent.Type.HoverEnter:
            self._set_hover(True)
        elif e.type() == QEvent.Type.HoverLeave:
            self._set_hover(False)
        return super().event(e)

    def eventFilter(self, obj, event):
        if obj is self.edit and event.type() == QEvent.Type.FocusIn:
            self.board.raise_note(self)
        return False

    def moveEvent(self, e):
        super().moveEvent(e)
        self.board.update()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._path = None
        self._place_grip()
        self.board.update()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.board.raise_note(self)
            self._drag = (e.globalPosition().toPoint()
                          - self.mapToGlobal(QPoint(0, 0)))
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            e.accept()
        else:
            super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        if self._drag is not None and (e.buttons() & Qt.MouseButton.LeftButton):
            p = self.board.mapFromGlobal(e.globalPosition().toPoint() - self._drag)
            self.move(max(0, p.x()), max(0, p.y()))
            e.accept()

    def mouseReleaseEvent(self, e):
        if self._drag is not None:
            self._drag = None
            self.unsetCursor()
            self.board.note_geometry_changed()
            e.accept()

    def mouseDoubleClickEvent(self, e):
        e.accept()  # иначе двойной щелчок по стикеру создаст новый под ним

    def build_menu(self):
        ctl = self.board.ctl
        menu = QMenu(self)
        colors = menu.addMenu(T("m_color"))
        palette = ctl.sticker_palette()
        for i, name in enumerate(palette_names(palette)):
            act = colors.addAction(swatch_icon(palette_color(palette, i)), name)
            act.triggered.connect(lambda *_, ci=i: self.set_color(ci))
        act = menu.addAction(T("m_reminder"))
        act.triggered.connect(lambda *_: ctl.edit_reminder(self))
        if self.kind != "plan":
            act = menu.addAction(T("m_repeat"))
            act.triggered.connect(lambda *_: ctl.edit_repeat(self))
        act = menu.addAction(T("m_duplicate"))
        act.triggered.connect(lambda *_: ctl.duplicate_note(self))
        menu.addSeparator()
        if self.kind == "plan":
            act = menu.addAction(T("m_open_tomorrow"))
            act.triggered.connect(lambda *_: ctl.show_day(ctl.current.addDays(1)))
        if not ctl.viewing_today():
            act = menu.addAction(T("m_move_today"))
            act.triggered.connect(lambda *_: ctl.move_note(self, ctl.today))
        act = menu.addAction(T("m_move_to"))
        act.triggered.connect(lambda *_: ctl.move_note_pick(self))
        menu.addSeparator()
        act = menu.addAction(T("btn_done"))
        act.triggered.connect(lambda *_: ctl.complete_note(self))
        if self.kind != "plan":
            act = menu.addAction(T("btn_delete"))
            act.triggered.connect(lambda *_: ctl.delete_note(self))
        return menu

    def show_menu(self, global_pos):
        self.build_menu().exec(global_pos)

    def set_color(self, ci):
        self.ci = int(ci)
        self.update()
        self.board.note_changed()

    def to_dict(self):
        d = dict(self.extra)
        d.update({
            "id": self.note_id,
            "x": self.x(),
            "y": self.y(),
            "w": self.width(),
            "h": self.height(),
            "text": self.edit.toPlainText(),
            "ci": self.ci,
            "color": self.color,
            "created": self.created,
        })
        if self.source == "yandex":
            d["source"] = "yandex"
            d["yandex_uid"] = self.yandex_uid
        if self.kind:
            d["kind"] = self.kind
        if self.rid:
            d["rid"] = self.rid
        if self.remind:
            d["remind"] = dict(self.remind)
        if self.fired:
            d["fired"] = list(self.fired)
        return d


# ------------------------------- Доска ----------------------------------
class Board(QWidget):
    def __init__(self, ctl):
        super().__init__()
        self.ctl = ctl
        self.notes = []
        self._loading = False

    # --- содержимое ---
    def clear(self):
        for n in self.notes:
            n.hide()
            n.setParent(None)
            n.deleteLater()
        self.notes = []

    def load(self, items):
        self._loading = True
        try:
            self.clear()
            for item in items:
                self._make(item)
        finally:
            self._loading = False
        self.update_extent()
        self.update()

    def _make(self, data):
        note = NoteWidget(self, data)
        note.show()
        self.notes.append(note)
        return note

    def add_note(self, data, focus=False):
        note = self._make(data)
        note.raise_()
        self.update_extent()
        if focus:
            note.edit.setFocus()
        self.ctl.board_changed()
        return note

    def remove_note(self, note):
        if note in self.notes:
            self.notes.remove(note)
            note.hide()
            note.setParent(None)
            note.deleteLater()
            self.update_extent()
            self.update()
            self.ctl.board_changed()

    def find_note(self, note_id):
        for n in self.notes:
            if n.note_id == note_id:
                return n
        return None

    def items(self):
        return [n.to_dict() for n in self.notes]

    def rects(self):
        return [(n.x(), n.y(), n.width(), n.height()) for n in self.notes]

    def avail_width(self):
        return self.ctl.board_scroll.viewport().width()

    def restyle(self):
        for n in self.notes:
            n.apply_font()
            n.update()
        self.update()

    # --- события от заметок ---
    def raise_note(self, note):
        note.raise_()
        if note in self.notes and self.notes[-1] is not note:
            self.notes.remove(note)
            self.notes.append(note)
            self.ctl.schedule_save()

    def note_changed(self):
        if not self._loading:
            self.ctl.schedule_save()

    def note_geometry_changed(self):
        self.update_extent()
        self.ctl.schedule_save()

    def update_extent(self):
        w = max((n.x() + n.width() for n in self.notes), default=0) + 40
        h = max((n.y() + n.height() for n in self.notes), default=0) + 40
        self.setMinimumSize(w, h)

    def tidy(self):
        if not self.notes:
            return
        order = sorted(self.notes, key=lambda n: (n.y() // 90, n.x()))
        spots = flow_layout([(n.width(), n.height()) for n in order],
                            self.avail_width())
        for note, (x, y) in zip(order, spots):
            note.move(x, y)
        self.update_extent()
        self.ctl.board_changed()

    # --- мышь и отрисовка ---
    def mouseDoubleClickEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            pos = e.position().toPoint()
            self.ctl.new_note(pos.x() - NOTE_W // 2, pos.y() - 24)

    def paintEvent(self, event):
        p = QPainter(self)
        area = event.rect()
        p.drawTiledPixmap(area, kraft_texture(), area.topLeft())
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.ctl.cfg.get("flowers", True):
            fl = dried_flowers_pixmap(self.devicePixelRatioF())
            fw = fl.width() / fl.devicePixelRatio()
            fh = fl.height() / fl.devicePixelRatio()
            p.drawPixmap(QPointF(self.width() - fw - 6, self.height() - fh + 4), fl)
        if self.notes:
            shade = C("shadow")
            p.setPen(Qt.PenStyle.NoPen)
            for n in self.notes:
                path = n.paper_path().translated(n.x(), n.y())
                for dx, dy, a in ((1.5, 7, 9), (1, 5, 13), (0.6, 3, 19), (0.3, 1.5, 26)):
                    shade.setAlpha(a)
                    p.setBrush(shade)
                    p.drawPath(path.translated(dx, dy))
            return

        # пустая доска
        r = self.rect()
        p.setFont(script_font(30))
        p.setPen(C("board_ink"))
        p.drawText(QRectF(0, r.height() * 0.34, r.width(), 54),
                   Qt.AlignmentFlag.AlignCenter, T("empty_quote"))
        small = QFont(ui_family())
        small.setPixelSize(13)
        p.setFont(small)
        p.setPen(C("board_muted"))
        p.drawText(QRectF(0, r.height() * 0.34 + 60, r.width(), 24),
                   Qt.AlignmentFlag.AlignCenter, T("empty_hint"))


# ----------------------------- Календарь --------------------------------
def current_qlocale():
    if LANG == "ru":
        return QLocale(QLocale.Language.Russian, QLocale.Country.Russia)
    return QLocale(QLocale.Language.English, QLocale.Country.UnitedKingdom)


class Calendar(QCalendarWidget):
    """Месяц без рамок: выбранный день — кружок, дни с заметками — точка."""

    def __init__(self, counts):
        super().__init__()
        self.counts = counts
        self.setGridVisible(False)
        self.setNavigationBarVisible(False)
        self.setDateEditEnabled(False)
        self.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.setHorizontalHeaderFormat(QCalendarWidget.HorizontalHeaderFormat.ShortDayNames)
        self.setFirstDayOfWeek(Qt.DayOfWeek.Monday)
        self.setLocale(current_qlocale())
        view = self.findChild(QTableView, "qt_calendar_calendarview")
        if view is not None:
            view.viewport().setAutoFillBackground(False)
            view.setAutoFillBackground(False)
            view.setStyleSheet("QTableView { background: transparent; border: none; }")
        self.setAutoFillBackground(False)

    def apply_theme(self):
        clear = QColor(0, 0, 0, 0)
        head = QTextCharFormat()
        head.setForeground(C("muted"))
        head.setBackground(clear)
        self.setHeaderTextFormat(head)
        day = QTextCharFormat()
        day.setForeground(C("muted"))
        day.setBackground(clear)
        for wd in (Qt.DayOfWeek.Monday, Qt.DayOfWeek.Tuesday, Qt.DayOfWeek.Wednesday,
                   Qt.DayOfWeek.Thursday, Qt.DayOfWeek.Friday, Qt.DayOfWeek.Saturday,
                   Qt.DayOfWeek.Sunday):
            self.setWeekdayTextFormat(wd, day)
        self.updateCells()

    def paintCell(self, painter, rect, date):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        active, archived = self.counts(date.toString("yyyy-MM-dd"))
        selected = date == self.selectedDate()
        today = date == QDate.currentDate()
        other = date.month() != self.monthShown()

        r = QRectF(rect)
        d = min(r.width(), r.height()) - 4
        circle = QRectF(r.center().x() - d / 2, r.center().y() - d / 2, d, d)
        if selected:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(C("accent"))
            painter.drawEllipse(circle)
        elif today:
            painter.setPen(QPen(C("accent"), 1.4))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(circle.adjusted(0.7, 0.7, -0.7, -0.7))

        if selected:
            color = C("on_accent")
        elif other:
            color = C("faint")
        elif today:
            color = C("accent")
        else:
            color = C("ink")
        font = QFont(painter.font())
        font.setPixelSize(13)
        font.setBold(selected or today)
        painter.setFont(font)
        painter.setPen(color)
        painter.drawText(circle, Qt.AlignmentFlag.AlignCenter, str(date.day()))

        if active or archived:
            if selected:
                dot = C("on_accent")
            elif active and not other:
                dot = C("rust")
            else:
                dot = C("faint")
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(dot)
            painter.drawEllipse(
                QPointF(circle.center().x(), circle.bottom() - 4.5), 1.7, 1.7)
        painter.restore()


# ------------------------------- Архив ----------------------------------
class ArchiveCard(QFrame):
    def __init__(self, ctl, data):
        super().__init__()
        self.ctl = ctl
        self.data = data
        self.seed = note_seed(data.get("id"))
        self._path = None
        ci = data.get("ci")
        ci = ci if isinstance(ci, int) else color_index(data.get("color"))
        self.color = palette_color(ctl.sticker_palette(), ci)
        self.setStyleSheet(
            "QLabel { color: #33281E; background: transparent; }"
            "QPushButton { border: none; background: rgba(255,255,255,120);"
            " color: #33281E; border-radius: 6px; padding: 4px 10px; font-size: 12px; }"
            "QPushButton:hover { background: rgba(255,255,255,215); }")
        v = QVBoxLayout(self)
        v.setContentsMargins(14, 12, 14, 12)
        v.setSpacing(8)

        text = (data.get("text") or "").strip() or T("empty")
        if len(text) > 400:
            text = text[:400].rstrip() + "…"
        label = QLabel(text)
        label.setTextFormat(Qt.TextFormat.PlainText)
        label.setWordWrap(True)
        fam, size = ctl.note_font()
        f = QFont(fam)
        f.setPixelSize(max(11, size - 1))
        label.setFont(f)
        v.addWidget(label)

        row = QHBoxLayout()
        row.setSpacing(6)
        note_id = data.get("id")
        back = QPushButton(T("restore"))
        back.setCursor(Qt.CursorShape.PointingHandCursor)
        back.clicked.connect(lambda *_: self.ctl.restore_archived(note_id))
        drop = QPushButton(T("delete"))
        drop.setCursor(Qt.CursorShape.PointingHandCursor)
        drop.clicked.connect(lambda *_: self.ctl.delete_archived(note_id))
        row.addWidget(back)
        row.addWidget(drop)
        row.addStretch(1)
        v.addLayout(row)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._path = None

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self._path is None:
            self._path = torn_path(QRectF(self.rect()).adjusted(2, 2, -2, -3),
                                   self.seed, amp=2.0)
        shade = C("shadow")
        shade.setAlpha(28)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(shade)
        p.drawPath(self._path.translated(0.5, 2))
        paint_paper(p, self._path, QColor(self.color), self.seed)


class ArchivePanel(PaperPanel):
    def __init__(self, ctl):
        super().__init__("left", "ArchivePanel")
        self.ctl = ctl
        self.setFixedWidth(310)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(26, 18, 8, 12)
        outer.setSpacing(10)
        title = QLabel(T("done_title"))
        title.setFont(serif_font(21))
        outer.addWidget(title)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.inner = QWidget()
        self.vbox = QVBoxLayout(self.inner)
        self.vbox.setContentsMargins(0, 0, 10, 0)
        self.vbox.setSpacing(12)
        self.vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.inner)
        outer.addWidget(self.scroll_area, 1)

    def refresh(self, items):
        while self.vbox.count():
            item = self.vbox.takeAt(0)
            w = item.widget() if item is not None else None
            if w is not None:
                w.hide()
                w.deleteLater()
        if not items:
            empty = QLabel(T("archive_empty"))
            empty.setObjectName("Hint")
            empty.setWordWrap(True)
            self.vbox.addWidget(empty)
            return
        for data in reversed(items):
            self.vbox.addWidget(ArchiveCard(self.ctl, data))


# ---------------------------- Диалоги -----------------------------------
class PaperDialog(QDialog):
    """Диалог на кремовой бумаге."""

    def __init__(self, parent, title):
        super().__init__(parent)
        self.setWindowTitle(title)

    def paintEvent(self, event):
        p = QPainter(self)
        p.drawTiledPixmap(self.rect(), paper_texture())


def make_title(text, size=21):
    lbl = QLabel(text)
    lbl.setFont(serif_font(size))
    return lbl


def make_section(text):
    lbl = QLabel(text.upper())
    lbl.setObjectName("Section")
    lbl.setFont(spaced_font(10, 1.3))
    return lbl


def dialog_buttons(ok_text, on_ok, on_cancel):
    row = QHBoxLayout()
    row.addStretch(1)
    cancel = QPushButton(T("cancel"))
    cancel.setCursor(Qt.CursorShape.PointingHandCursor)
    cancel.clicked.connect(lambda *_: on_cancel())
    ok = QPushButton(ok_text)
    ok.setObjectName("Primary")
    ok.setDefault(True)
    ok.setCursor(Qt.CursorShape.PointingHandCursor)
    ok.clicked.connect(lambda *_: on_ok())
    row.addWidget(cancel)
    row.addWidget(ok)
    return row


class MoveDialog(PaperDialog):
    """Выбор дня, на который перенести заметку."""

    def __init__(self, ctl, current):
        super().__init__(ctl, T("move_title"))
        self.result_date = None
        self.setMinimumWidth(380)
        v = QVBoxLayout(self)
        v.setContentsMargins(24, 20, 24, 18)
        v.setSpacing(10)
        v.addWidget(make_title(T("move_title")))
        hint = QLabel(T("move_hint"))
        hint.setObjectName("Hint")
        v.addWidget(hint)

        quick = QHBoxLayout()
        quick.setSpacing(6)
        today = ctl.today
        days_to_monday = (8 - today.dayOfWeek()) % 7 or 7
        options = [(T("tomorrow"), today.addDays(1)),
                   (T("q_day_after"), today.addDays(2)),
                   (T("q_monday"), today.addDays(days_to_monday)),
                   (T("q_week"), today.addDays(7))]
        for text, d in options:
            b = QPushButton(text)
            b.setObjectName("Quick")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda *_, dd=d: self.calendar.setSelectedDate(dd))
            quick.addWidget(b)
        quick.addStretch(1)
        v.addLayout(quick)

        nav = QHBoxLayout()
        self.month = QLabel()
        self.month.setObjectName("MonthLabel")
        prev_m = ctl._nav_button("‹", T("prev_month"))
        next_m = ctl._nav_button("›", T("next_month"))
        nav.addWidget(self.month)
        nav.addStretch(1)
        nav.addWidget(prev_m)
        nav.addWidget(next_m)
        v.addLayout(nav)

        self.calendar = Calendar(ctl.store.counts)
        self.calendar.apply_theme()
        self.calendar.setFixedHeight(232)
        self.calendar.currentPageChanged.connect(self._page)
        self.calendar.setSelectedDate(current.addDays(1))
        self.calendar.activated.connect(lambda *_: self._ok())
        prev_m.clicked.connect(lambda *_: self.calendar.showPreviousMonth())
        next_m.clicked.connect(lambda *_: self.calendar.showNextMonth())
        self._page(self.calendar.yearShown(), self.calendar.monthShown())
        v.addWidget(self.calendar)
        v.addLayout(dialog_buttons(T("move_btn"), self._ok, self.reject))

    def _page(self, year, month):
        self.month.setText(f"{MONTHS_NOM[LANG][month - 1]} {year}")

    def _ok(self):
        self.result_date = self.calendar.selectedDate()
        self.accept()


def make_time_edit(text):
    te = QTimeEdit()
    te.setDisplayFormat("HH:mm")
    hm = parse_hm(text) or (10, 0)
    te.setTime(QTime(hm[0], hm[1]))
    te.setFixedWidth(92)
    return te


class ReminderDialog(PaperDialog):
    """Напоминание-будильник для заметки."""

    def __init__(self, ctl, note_day, created, remind):
        super().__init__(ctl, T("rem_title"))
        self.outcome = "cancel"
        self.remind = None
        self.setMinimumWidth(440)
        cfg = ctl.cfg
        morning = cfg.get("remind_morning", DEFAULT_MORNING)
        evening = cfg.get("remind_evening", DEFAULT_EVENING)
        now = datetime.now()
        mode, times = default_reminder(note_day, created, now, morning, evening)
        if remind and remind.get("times"):
            times = list(remind["times"])
            mode = "twice" if len(times) >= 2 else "once"

        v = QVBoxLayout(self)
        v.setContentsMargins(24, 20, 24, 18)
        v.setSpacing(10)
        v.addWidget(make_title(T("rem_title")))

        self.group = QButtonGroup(self)
        self.r_twice = QRadioButton(T("rem_twice"))
        self.r_once = QRadioButton(T("rem_once"))
        self.r_off = QRadioButton(T("rem_off"))
        for i, rb in enumerate((self.r_twice, self.r_once, self.r_off)):
            self.group.addButton(rb, i)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)
        tw = times if mode == "twice" else [morning, evening]
        self.t_morning = make_time_edit(tw[0])
        self.t_evening = make_time_edit(tw[-1])
        self.t_once = make_time_edit(times[0] if mode == "once" else evening)
        grid.addWidget(self.r_twice, 0, 0)
        lm = QLabel(T("rem_morning"))
        lm.setObjectName("Hint")
        le = QLabel(T("rem_evening"))
        le.setObjectName("Hint")
        grid.addWidget(lm, 0, 1)
        grid.addWidget(self.t_morning, 0, 2)
        grid.addWidget(le, 0, 3)
        grid.addWidget(self.t_evening, 0, 4)
        grid.addWidget(self.r_once, 1, 0)
        la = QLabel(T("rem_at"))
        la.setObjectName("Hint")
        grid.addWidget(la, 1, 1)
        grid.addWidget(self.t_once, 1, 2)
        grid.addWidget(self.r_off, 2, 0)
        grid.setColumnStretch(5, 1)
        v.addLayout(grid)

        hints = []
        if created and created.date() == note_day and created.hour >= 12:
            hints.append(T("rem_hint_after12"))
        else:
            hints.append(T("rem_hint_twice"))
        if note_day != now.date():
            hints.append(T("rem_hint_day", d=human_date_inline(note_day, now.date())))
        hint = QLabel("\n".join(hints))
        hint.setObjectName("Hint")
        hint.setWordWrap(True)
        v.addWidget(hint)

        (self.r_twice if mode == "twice" else self.r_once).setChecked(True)
        self.group.idToggled.connect(lambda *_: self._sync())
        self._sync()
        v.addSpacing(4)
        v.addLayout(dialog_buttons(T("save"), self._ok, self.reject))

    def _sync(self):
        twice = self.r_twice.isChecked()
        once = self.r_once.isChecked()
        self.t_morning.setEnabled(twice)
        self.t_evening.setEnabled(twice)
        self.t_once.setEnabled(once)

    def _ok(self):
        now = datetime.now().isoformat(timespec="seconds")
        if self.r_off.isChecked():
            self.remind = None
        elif self.r_twice.isChecked():
            times = sorted({self.t_morning.time().toString("HH:mm"),
                            self.t_evening.time().toString("HH:mm")})
            self.remind = {"mode": "twice", "times": times, "since": now}
        else:
            self.remind = {"mode": "once",
                           "times": [self.t_once.time().toString("HH:mm")],
                           "since": now}
        self.outcome = "ok"
        self.accept()


class RepeatDialog(PaperDialog):
    """Выбор дней, в которые заметка повторяется."""

    def __init__(self, ctl, note_day, rule):
        super().__init__(ctl, T("rep_title"))
        self.outcome = "cancel"
        self.rule = None
        self.setMinimumWidth(440)
        rule = normalize_rule(rule)
        v = QVBoxLayout(self)
        v.setContentsMargins(24, 20, 24, 18)
        v.setSpacing(10)
        v.addWidget(make_title(T("rep_title")))

        self.group = QButtonGroup(self)
        self.r_none = QRadioButton(T("rep_none"))
        self.r_daily = QRadioButton(T("rep_daily"))
        self.r_weekdays = QRadioButton(T("rep_weekdays"))
        self.r_days = QRadioButton(T("rep_days"))
        self.dom = note_day.day
        self.r_monthly = QRadioButton(T("rep_monthly", n=self.dom))
        for i, rb in enumerate((self.r_none, self.r_daily, self.r_weekdays,
                                self.r_days, self.r_monthly)):
            self.group.addButton(rb, i)
        for rb in (self.r_none, self.r_daily, self.r_weekdays, self.r_days):
            v.addWidget(rb)
        row = QHBoxLayout()
        row.setContentsMargins(26, 0, 0, 4)
        row.setSpacing(6)
        self.day_btns = []
        chosen = set(rule["days"]) if rule and rule["kind"] == "days" else {note_day.weekday()}
        for d in range(7):
            b = QPushButton(WEEKDAYS_SHORT[LANG][d])
            b.setObjectName("Day")
            b.setCheckable(True)
            b.setChecked(d in chosen)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.toggled.connect(lambda *_: self.r_days.setChecked(True))
            self.day_btns.append(b)
            row.addWidget(b)
        row.addStretch(1)
        v.addLayout(row)
        v.addWidget(self.r_monthly)

        hint = QLabel(T("rep_hint", d=human_date_inline(note_day, qdate_to_py(ctl.today))))
        hint.setObjectName("Hint")
        hint.setWordWrap(True)
        v.addWidget(hint)
        kind = rule["kind"] if rule else None
        {None: self.r_none, "daily": self.r_daily, "weekdays": self.r_weekdays,
         "days": self.r_days, "monthly": self.r_monthly}[kind].setChecked(True)
        if kind is None:
            self.r_none.setChecked(True)
        v.addSpacing(4)
        v.addLayout(dialog_buttons(T("save"), self._ok, self.reject))

    def _ok(self):
        if self.r_daily.isChecked():
            self.rule = {"kind": "daily"}
        elif self.r_weekdays.isChecked():
            self.rule = {"kind": "weekdays"}
        elif self.r_days.isChecked():
            days = [d for d, b in enumerate(self.day_btns) if b.isChecked()]
            self.rule = {"kind": "days", "days": days} if days else None
        elif self.r_monthly.isChecked():
            self.rule = {"kind": "monthly", "dom": self.dom}
        else:
            self.rule = None
        self.outcome = "ok"
        self.accept()


class SettingsPreview(QWidget):
    """Живой образец стикера с выбранными палитрой и шрифтом."""

    def __init__(self, dlg):
        super().__init__()
        self.dlg = dlg
        self.setFixedHeight(122)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect())
        p.drawTiledPixmap(self.rect(), kraft_texture())
        palette = self.dlg.chosen_palette()
        fam, size = self.dlg.chosen_font()
        colors = PALETTES[palette]["colors"]
        rect = QRectF(16, 16, 236, r.height() - 28)
        path = torn_path(rect, 77)
        shade = C("shadow")
        shade.setAlpha(30)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(shade)
        p.drawPath(path.translated(1, 4))
        paint_paper(p, path, QColor(colors[0]), 77)
        draw_tape(p, rect.left() + 80, rect.top() + 1, -3)
        f = QFont(fam)
        f.setPixelSize(size)
        p.setFont(f)
        p.setPen(QColor(NOTE_INK))
        p.drawText(rect.adjusted(14, 16, -10, -8),
                   int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
                   | int(Qt.TextFlag.TextWordWrap), T("set_preview"))
        # остальные цвета палитры — маленькими листочками
        x = rect.right() + 22
        for i, c in enumerate(colors[1:]):
            sr = QRectF(x + i * 44, 30 + (i % 2) * 12, 36, 48)
            if sr.right() > r.right() - 8:
                break
            sp = torn_path(sr, 500 + i, amp=1.6, step=4)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(shade)
            p.drawPath(sp.translated(0.5, 2.5))
            paint_paper(p, sp, QColor(c), 500 + i,
                        PALETTES[palette].get("grid") == i + 1)


class SettingsDialog(PaperDialog):
    def __init__(self, ctl):
        super().__init__(ctl, T("set_title"))
        self.ctl = ctl
        cfg = ctl.cfg
        self.setMinimumWidth(600)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 16)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        body = QWidget()
        v = QVBoxLayout(body)
        v.setContentsMargins(28, 22, 28, 8)
        v.setSpacing(10)
        scroll.setWidget(body)
        outer.addWidget(scroll, 1)

        v.addWidget(make_title(T("set_title"), 26))
        v.addSpacing(4)

        # --- внешний вид ---
        v.addWidget(make_section(T("set_look")))
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        form.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(9)
        self.lang_box = QComboBox()
        self.lang_box.addItem("Русский", "ru")
        self.lang_box.addItem("English", "en")
        self.lang_box.setCurrentIndex(0 if LANG == "ru" else 1)
        form.addRow(T("set_lang"), self.lang_box)
        self.theme_box = QComboBox()
        self.theme_box.addItem(T("theme_light"), "light")
        self.theme_box.addItem(T("theme_dark"), "dark")
        self.theme_box.setCurrentIndex(1 if Theme.name == "dark" else 0)
        form.addRow(T("set_theme"), self.theme_box)
        self.palette_box = QComboBox()
        self.palette_box.setIconSize(QSize(84, 16))
        for pid in PALETTE_ORDER:
            name = PALETTES[pid]["name"][0 if LANG == "ru" else 1]
            self.palette_box.addItem(palette_strip_icon(pid), name, pid)
        self.palette_box.setCurrentIndex(max(0, PALETTE_ORDER.index(ctl.sticker_palette())))
        form.addRow(T("set_palette"), self.palette_box)
        fam, size = ctl.note_font()
        font_row = QHBoxLayout()
        self.font_box = QComboBox()
        self.font_box.setMinimumWidth(230)
        self.font_box.setMaxVisibleItems(24)
        self._fill_fonts()
        self.font_full = QFontComboBox()
        self.font_full.setWritingSystem(QFontDatabase.WritingSystem.Cyrillic)
        self.font_full.setCurrentFont(QFont(fam))
        idx = self.font_box.findData(fam)
        if idx < 0:
            idx = self.font_box.findData(OTHER_FONT)
        self.font_box.setCurrentIndex(idx)
        self.size_box = QSpinBox()
        self.size_box.setRange(10, 24)
        self.size_box.setValue(size)
        self.size_box.setSuffix(" px")
        font_row.addWidget(self.font_box, 1)
        font_row.addWidget(self.size_box)
        form.addRow(T("set_font"), font_row)
        form.addRow("", self.font_full)
        v.addLayout(form)
        self.font_box.currentIndexChanged.connect(lambda *_: self._sync_font())
        self.font_full.currentFontChanged.connect(lambda *_: self.preview.update())

        self.preview = SettingsPreview(self)
        v.addWidget(self.preview)
        self.flowers_box = QCheckBox(T("set_flowers"))
        self.flowers_box.setChecked(bool(cfg.get("flowers", True)))
        v.addWidget(self.flowers_box)
        for box in (self.palette_box, self.font_box):
            box.currentIndexChanged.connect(lambda *_: self.preview.update())
        self._sync_font()
        self.size_box.valueChanged.connect(lambda *_: self.preview.update())
        v.addSpacing(8)

        # --- напоминания ---
        v.addWidget(make_section(T("set_reminders")))
        rem = QHBoxLayout()
        rem.setSpacing(8)
        self.t_morning = make_time_edit(cfg.get("remind_morning", DEFAULT_MORNING))
        self.t_evening = make_time_edit(cfg.get("remind_evening", DEFAULT_EVENING))
        self.t_plan = make_time_edit(cfg.get("plan_time", DEFAULT_PLAN_TIME))
        for text, te in ((T("set_morning"), self.t_morning),
                         (T("set_evening"), self.t_evening),
                         (T("set_plan"), self.t_plan)):
            rem.addWidget(QLabel(text))
            rem.addWidget(te)
            rem.addSpacing(10)
        rem.addStretch(1)
        v.addLayout(rem)
        plan_hint = QLabel(T("set_plan_hint"))
        plan_hint.setObjectName("Hint")
        plan_hint.setWordWrap(True)
        v.addWidget(plan_hint)
        v.addSpacing(8)

        # --- Яндекс ---
        v.addWidget(make_section(T("set_yandex")))
        accent = Theme.colors["accent"]
        link = (f'<a style="color:{accent}" '
                'href="https://id.yandex.ru/security/app-passwords">'
                "id.yandex.ru/security/app-passwords</a>")
        info = QLabel(T("set_yandex_info", link=link))
        info.setObjectName("Hint")
        info.setWordWrap(True)
        info.setOpenExternalLinks(True)
        v.addWidget(info)
        yform = QFormLayout()
        yform.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        yform.setHorizontalSpacing(16)
        yform.setVerticalSpacing(8)
        self.username_edit = QLineEdit(cfg.get("username", ""))
        self.username_edit.setPlaceholderText("login@yandex.ru")
        self.password_edit = QLineEdit(cfg.get("password", ""))
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        yform.addRow(T("set_login"), self.username_edit)
        yform.addRow(T("set_password"), self.password_edit)
        v.addLayout(yform)
        v.addSpacing(8)

        # --- система ---
        v.addWidget(make_section(T("set_system")))
        self._autostart_was = autostart_enabled()
        self.autostart_box = QCheckBox(T("set_autostart"))
        self.autostart_box.setChecked(self._autostart_was)
        self.autostart_box.setEnabled(IS_WIN or IS_MAC or IS_LINUX)
        v.addWidget(self.autostart_box)
        row = QHBoxLayout()
        shortcut_btn = QPushButton(T("set_shortcut"))
        shortcut_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        shortcut_btn.clicked.connect(lambda *_: self.make_shortcut())
        row.addWidget(shortcut_btn)
        shortcut_btn.setVisible(not FROZEN or not IS_MAC)
        row.addStretch(1)
        v.addLayout(row)
        v.addStretch(1)

        btns = dialog_buttons(T("save"), self.save_and_close, self.reject)
        btns.setContentsMargins(28, 0, 28, 0)
        outer.addLayout(btns)
        screen = QGuiApplication.primaryScreen()
        max_h = screen.availableGeometry().height() - 80 if screen else 800
        self.resize(640, min(max_h, body.sizeHint().height() + 70))

    def _fill_fonts(self):
        """Короткий список по группам; каждый шрифт показан своим начертанием."""
        box = self.font_box
        model = box.model()
        head_font = spaced_font(10, 1.2)
        for key, fams in curated_fonts():
            box.addItem(T(key), None)
            i = box.count() - 1
            item = model.item(i) if isinstance(model, QStandardItemModel) else None
            if item is not None:
                item.setFlags(Qt.ItemFlag.NoItemFlags)
            box.setItemData(i, head_font, Qt.ItemDataRole.FontRole)
            box.setItemData(i, C("muted"), Qt.ItemDataRole.ForegroundRole)
            for fam in fams:
                box.addItem("   " + fam, fam)
                f = QFont(fam)
                f.setPixelSize(15)
                box.setItemData(box.count() - 1, f, Qt.ItemDataRole.FontRole)
        box.addItem(T("font_other"), OTHER_FONT)

    def _sync_font(self):
        other = self.font_box.currentData() == OTHER_FONT
        self.font_full.setVisible(other)
        self.preview.update()

    def chosen_font(self):
        fam = self.font_box.currentData()
        if not fam or fam == OTHER_FONT:
            fam = self.font_full.currentFont().family()
        return fam, self.size_box.value()

    def chosen_palette(self):
        return self.palette_box.currentData() or DEFAULT_PALETTE

    def make_shortcut(self):
        ok, text = create_desktop_shortcut()
        if ok:
            QMessageBox.information(self, T("app"), text)
        else:
            QMessageBox.warning(self, T("app"), text)

    def save_and_close(self):
        cfg = self.ctl.cfg
        cfg["username"] = self.username_edit.text().strip()
        cfg["password"] = self.password_edit.text()
        cfg["remind_morning"] = self.t_morning.time().toString("HH:mm")
        cfg["remind_evening"] = self.t_evening.time().toString("HH:mm")
        cfg["plan_time"] = self.t_plan.time().toString("HH:mm")
        fam, size = self.chosen_font()
        cfg["note_font"] = fam
        cfg["note_font_size"] = size
        cfg["palette"] = self.chosen_palette()
        cfg["flowers"] = self.flowers_box.isChecked()
        theme = self.theme_box.currentData() or "light"
        lang = self.lang_box.currentData() or "ru"
        save_config(cfg)
        want = self.autostart_box.isChecked()
        if want != self._autostart_was:
            try:
                set_autostart(want)
            except Exception as e:
                QMessageBox.warning(self, T("app"), T("autostart_fail", e=e))
        self.accept()
        self.ctl.apply_settings(theme, lang)


# ------------------------ Всплывающее напоминание -----------------------
class ReminderPopup(QWidget):
    """Уведомление-листок в правом нижнем углу экрана."""

    W, H, M = 344, 176, 14  # размер листка и поля под тень

    def __init__(self, manager, note_id, day_key, text, when, ci, palette, font):
        super().__init__(None, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint
                         | Qt.WindowType.WindowStaysOnTopHint)
        self.manager = manager
        self.note_id = note_id
        self.day_key = day_key
        self.seed = note_seed(note_id)
        self.color = QColor(palette_color(palette, ci))
        self.grid = PALETTES.get(palette, {}).get("grid") == ci
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setFixedSize(self.W + 2 * self.M, self.H + 2 * self.M)
        self.setWindowTitle(T("popup_title"))

        v = QVBoxLayout(self)
        v.setContentsMargins(self.M + 20, self.M + 20, self.M + 14, self.M + 12)
        v.setSpacing(6)
        head = QHBoxLayout()
        title = QLabel(T("popup_title"))
        title.setFont(script_font(20))
        title.setStyleSheet("color: #33281E; background: transparent;")
        when_lbl = BellTag(self, clickable=False)
        when_lbl.set_text(when)
        close = QPushButton("✕")
        close.setToolTip(T("popup_close"))
        close.setFixedSize(24, 24)
        close.setCursor(Qt.CursorShape.PointingHandCursor)
        close.setStyleSheet(
            "QPushButton { border: none; background: transparent; color: rgba(51,40,30,150);"
            " padding: 0; font-size: 13px; }"
            "QPushButton:hover { background: rgba(60,40,20,30); border-radius: 12px; }")
        close.clicked.connect(lambda *_: self.dismiss())
        head.addWidget(title)
        head.addStretch(1)
        head.addWidget(when_lbl)
        head.addSpacing(4)
        head.addWidget(close)
        v.addLayout(head)

        body = QLabel()
        fam, size = font
        f = QFont(fam)
        f.setPixelSize(min(15, max(12, size)))
        body.setFont(f)
        body.setStyleSheet("color: #33281E; background: transparent;")
        body.setWordWrap(True)
        body.setTextFormat(Qt.TextFormat.PlainText)
        body.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        lines = (text or "").strip().splitlines() or [T("empty")]
        short = "\n".join(lines[:3])
        if len(short) > 150:
            short = short[:150].rstrip() + "…"
        body.setText(short)
        v.addWidget(body, 1)

        row = QHBoxLayout()
        row.setSpacing(6)
        style = ("QPushButton { border: 1px solid rgba(51,40,30,60);"
                 " background: rgba(255,255,255,120); color: #33281E; border-radius: 6px;"
                 " padding: 4px 10px; font-size: 12px; }"
                 "QPushButton:hover { background: rgba(255,255,255,220); }")
        for label, kind in ((T("popup_done"), "done"),
                            (T("popup_snooze", n=SNOOZE_MINUTES), "snooze"),
                            (T("popup_open"), "open")):
            b = QPushButton(label)
            b.setStyleSheet(style)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda *_, k=kind: self.manager.action(k, self))
            row.addWidget(b)
        row.addStretch(1)
        v.addLayout(row)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.M, self.M + 6, self.W, self.H - 6)
        path = torn_path(rect, self.seed)
        p.setPen(Qt.PenStyle.NoPen)
        for dx, dy, a in ((0, 8, 12), (0, 5, 18), (0, 3, 26), (0, 1.5, 34)):
            p.setBrush(QColor(30, 20, 10, a))
            p.drawPath(path.translated(dx, dy))
        paint_paper(p, path, self.color, self.seed, self.grid)
        draw_tape(p, self.M + self.W * 0.5, self.M + 6, -2.5)

    def dismiss(self):
        self.manager.closed(self)
        self.close()


class PopupManager(QObject):
    """Показывает уведомления стопкой в правом нижнем углу и звонит."""

    MAX_VISIBLE = 4

    def __init__(self, get_window):
        super().__init__()
        self.get_window = get_window
        self.popups = []
        self.queue = []
        self.offscreen = False

    def show(self, **kw):
        if len(self.popups) >= self.MAX_VISIBLE:
            self.queue.append(kw)
            return None
        popup = ReminderPopup(self, **kw)
        if self.offscreen:
            popup.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
        self.popups.append(popup)
        self._layout(popup, animate=True)
        popup.show()
        if not self.offscreen:
            self._ring()
        return popup

    def _ring(self):
        try:
            if IS_WIN:
                import winsound
                winsound.MessageBeep(0x40)
                return
            sounds = ([["afplay", "/System/Library/Sounds/Glass.aiff"]] if IS_MAC else
                      [["canberra-gtk-play", "-i", "message-new-instant"],
                       ["paplay", "/usr/share/sounds/freedesktop/stereo/message-new-instant.oga"]])
            for cmd in sounds:
                if shutil.which(cmd[0]):
                    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return
            QApplication.beep()
        except Exception:
            pass

    def _target(self, index, popup):
        screen = QGuiApplication.primaryScreen()
        area = screen.availableGeometry() if screen else QRect(0, 0, 1280, 800)
        x = area.right() - popup.width() - 4
        y = area.bottom() - (index + 1) * (popup.height() - 18) - 4
        return QPoint(x, y)

    def _layout(self, new=None, animate=False):
        for i, popup in enumerate(self.popups):
            target = self._target(i, popup)
            if popup is new and animate and not self.offscreen:
                popup.move(target + QPoint(60, 0))
                popup.setWindowOpacity(0.0)
                anim = QPropertyAnimation(popup, QByteArray(b"pos"), popup)
                anim.setDuration(260)
                anim.setEndValue(target)
                anim.setEasingCurve(QEasingCurve.Type.OutCubic)
                fade = QPropertyAnimation(popup, QByteArray(b"windowOpacity"), popup)
                fade.setDuration(260)
                fade.setEndValue(1.0)
                anim.start()
                fade.start()
            else:
                popup.move(target)

    def closed(self, popup):
        if popup in self.popups:
            self.popups.remove(popup)
        self._layout()
        if self.queue and len(self.popups) < self.MAX_VISIBLE:
            self.show(**self.queue.pop(0))

    def action(self, kind, popup):
        win = self.get_window()
        try:
            if win is not None:
                win.reminder_action(kind, popup.note_id, popup.day_key)
        finally:
            popup.dismiss()

    def close_all(self):
        for popup in list(self.popups):
            popup.close()
        self.popups = []
        self.queue = []


# ------------------------- Яндекс: фоновый поток ------------------------
class YandexSyncWorker(QObject):
    finished = Signal(list)   # список событий
    error = Signal(str)

    def __init__(self, username, password, day):
        super().__init__()
        self.username = username
        self.password = password
        self.day = day

    def run(self):
        try:
            events = fetch_yandex_events(self.username, self.password, self.day)
            self.finished.emit(events)
        except Exception as e:
            traceback.print_exc()
            self.error.emit(str(e) or e.__class__.__name__)


# ---------------------------- Главное окно ------------------------------
def qdate_to_py(q):
    return pydate(q.year(), q.month(), q.day())


class MainWindow(QMainWindow):
    def __init__(self, store, cfg, popups, on_rebuild=None, selftest=False):
        super().__init__()
        self.store = store
        self.cfg = cfg
        self.popups = popups
        self.on_rebuild = on_rebuild
        self.selftest = selftest
        self.today = QDate.currentDate()
        self.current = self.today
        self.undo = {}
        self.tray = None
        self._loaded = False
        self._quitting = False
        self._sync_thread = None
        self._sync_worker = None
        self._sync_key = None

        self.setWindowTitle(T("app"))
        self.setWindowIcon(make_app_icon())
        self.setMinimumSize(1000, 600)
        self.resize(1280, 800)

        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(500)
        self._save_timer.timeout.connect(self.flush_and_save)
        self._status_timer = QTimer(self)
        self._status_timer.setSingleShot(True)
        self._status_timer.timeout.connect(lambda: self.status.setText(""))

        Theme.use(cfg.get("theme", "light"))
        self._build_ui()
        self._build_shortcuts()
        self._build_tray()
        self.apply_theme(Theme.name, save=False)
        self._restore_geometry()
        self.ensure_plan_note()
        self.show_day(self.today, flush=False)
        self._loaded = True

        self._clock = QTimer(self)
        self._clock.setInterval(20_000)
        self._clock.timeout.connect(self._tick)
        if not selftest:
            self._clock.start()
            QTimer.singleShot(2500, self.check_reminders)

    # ------------------------------------------------------- настройки
    def sticker_palette(self):
        pid = self.cfg.get("palette", DEFAULT_PALETTE)
        return pid if pid in PALETTES else DEFAULT_PALETTE

    def note_font(self):
        fam = self.cfg.get("note_font") or pick_family(NOTE_FONTS)
        size = _to_int(self.cfg.get("note_font_size"), 14)
        return fam, max(10, min(24, size))

    # ---------------------------------------------------------------- UI
    def _build_ui(self):
        root = QWidget()
        root.setObjectName("Root")
        root.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setCentralWidget(root)
        h = QHBoxLayout(root)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)
        h.addWidget(self._build_sidebar())
        h.addWidget(self._build_main(), 1)

    def _nav_button(self, text, tip):
        b = QPushButton(text)
        b.setObjectName("Nav")
        b.setFixedSize(30, 30)
        b.setToolTip(tip)
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        return b

    def _build_sidebar(self):
        side = PaperPanel("right", "Sidebar")
        side.setFixedWidth(300)
        v = QVBoxLayout(side)
        v.setContentsMargins(20, 14, 26, 12)
        v.setSpacing(10)

        self.app_title = QLabel(T("app"))
        self.app_title.setFont(script_font(34))
        v.addWidget(self.app_title)

        self.search = QLineEdit()
        self.search.setPlaceholderText(T("search"))
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(lambda *_: self.refresh_side_list())
        v.addWidget(self.search)
        v.addSpacing(6)

        nav = QHBoxLayout()
        nav.setSpacing(4)
        self.month_label = QLabel()
        self.month_label.setObjectName("MonthLabel")
        prev_m = self._nav_button("‹", T("prev_month"))
        next_m = self._nav_button("›", T("next_month"))
        nav.addWidget(self.month_label)
        nav.addStretch(1)
        nav.addWidget(prev_m)
        nav.addWidget(next_m)
        v.addLayout(nav)

        self.calendar = Calendar(self.store.counts)
        self.calendar.setFixedHeight(236)
        self.calendar.selectionChanged.connect(self._on_calendar_selection)
        self.calendar.currentPageChanged.connect(self._on_page_changed)
        prev_m.clicked.connect(lambda *_: self.calendar.showPreviousMonth())
        next_m.clicked.connect(lambda *_: self.calendar.showNextMonth())
        v.addWidget(self.calendar)
        v.addSpacing(8)

        self.section = QLabel(T("found"))
        self.section.setObjectName("Section")
        self.section.setFont(spaced_font(10, 1.3))
        v.addWidget(self.section)

        self.side_list = QListWidget()
        self.side_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.side_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.side_list.setCursor(Qt.CursorShape.PointingHandCursor)
        self.side_list.itemClicked.connect(self._on_side_item)
        v.addWidget(self.side_list, 1)
        # пустое место вместо списка, когда ничего не ищут
        self.side_filler = QWidget()
        self.side_filler.setSizePolicy(QSizePolicy.Policy.Preferred,
                                       QSizePolicy.Policy.Expanding)
        v.addWidget(self.side_filler, 1)

        self.carry_btn = QPushButton(T("carry_btn"))
        self.carry_btn.setToolTip(T("carry_tip"))
        self.carry_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.carry_btn.clicked.connect(lambda *_: self.carry_over())
        v.addWidget(self.carry_btn)

        bottom = QHBoxLayout()
        bottom.setSpacing(2)
        settings_btn = QPushButton(T("settings"))
        settings_btn.setObjectName("Flat")
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.clicked.connect(lambda *_: self.open_settings())
        self.theme_btn = QPushButton(T("dark_theme"))
        self.theme_btn.setObjectName("Flat")
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.clicked.connect(lambda *_: self.toggle_theme())
        bottom.addWidget(settings_btn)
        bottom.addStretch(1)
        bottom.addWidget(self.theme_btn)
        v.addLayout(bottom)
        return side

    def _build_main(self):
        main = QWidget()
        v = QVBoxLayout(main)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        header = PaperPanel("bottom", "Header")
        hv = QVBoxLayout(header)
        hv.setContentsMargins(30, 18, 24, 20)
        hv.setSpacing(12)

        row1 = QHBoxLayout()
        titles = QVBoxLayout()
        titles.setSpacing(0)
        self.weekday_label = QLabel()
        self.weekday_label.setObjectName("Weekday")
        self.weekday_label.setFont(spaced_font(11, 1.6))
        self.date_label = QLabel()
        self.date_label.setFont(serif_font(34))
        self.stats_label = QLabel()
        self.stats_label.setObjectName("Stats")
        titles.addWidget(self.weekday_label)
        titles.addWidget(self.date_label)
        titles.addWidget(self.stats_label)
        row1.addLayout(titles)
        row1.addStretch(1)

        day_nav = QHBoxLayout()
        day_nav.setSpacing(6)
        prev_d = self._nav_button("‹", T("prev_day"))
        next_d = self._nav_button("›", T("next_day"))
        self.today_btn = QPushButton(T("today"))
        self.today_btn.setObjectName("Compact")
        self.today_btn.setFixedHeight(30)
        self.today_btn.setToolTip(T("today_tip"))
        self.today_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        prev_d.clicked.connect(lambda *_: self.show_day(self.current.addDays(-1)))
        next_d.clicked.connect(lambda *_: self.show_day(self.current.addDays(1)))
        self.today_btn.clicked.connect(lambda *_: self.go_today())
        day_nav.addWidget(prev_d)
        day_nav.addWidget(self.today_btn)
        day_nav.addWidget(next_d)
        nav_box = QVBoxLayout()
        nav_box.addLayout(day_nav)
        nav_box.addStretch(1)
        row1.addLayout(nav_box)
        hv.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(8)
        self.new_btn = QPushButton(T("new_note"))
        self.new_btn.setObjectName("Primary")
        self.new_btn.setToolTip(T("new_note_tip"))
        self.new_btn.clicked.connect(lambda *_: self.new_note())
        self.tidy_btn = QPushButton(T("tidy"))
        self.tidy_btn.setToolTip(T("tidy_tip"))
        self.tidy_btn.clicked.connect(lambda *_: self.board.tidy())
        self.sync_btn = QPushButton(T("yandex"))
        self.sync_btn.setToolTip(T("yandex_tip"))
        self.sync_btn.clicked.connect(lambda *_: self.sync_yandex())
        self.undo_btn = QPushButton(T("undo"))
        self.undo_btn.setToolTip(T("undo_tip"))
        self.undo_btn.clicked.connect(lambda *_: self.undo_last())
        self.status = QLabel("")
        self.status.setObjectName("Status")
        self.status.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.archive_btn = QPushButton(T("archive"))
        self.archive_btn.setCheckable(True)
        self.archive_btn.setToolTip(T("archive_tip"))
        self.archive_btn.toggled.connect(lambda on: self._toggle_archive(on))
        for b in (self.new_btn, self.tidy_btn, self.sync_btn, self.undo_btn,
                  self.archive_btn):
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        row2.addWidget(self.new_btn)
        row2.addWidget(self.tidy_btn)
        row2.addWidget(self.sync_btn)
        row2.addWidget(self.undo_btn)
        row2.addSpacing(8)
        row2.addWidget(self.status, 1)
        row2.addWidget(self.archive_btn)
        hv.addLayout(row2)
        v.addWidget(header)

        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)
        self.board = Board(self)
        self.board_scroll = QScrollArea()
        self.board_scroll.setWidgetResizable(True)
        self.board_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.board_scroll.setWidget(self.board)
        self.archive_panel = ArchivePanel(self)
        self.archive_panel.hide()
        content.addWidget(self.board_scroll, 1)
        content.addWidget(self.archive_panel)
        v.addLayout(content, 1)
        return main

    def _build_shortcuts(self):
        def bind(keys, fn):
            sc = QShortcut(QKeySequence(keys), self)
            sc.activated.connect(fn)
        bind("Ctrl+N", lambda: self.new_note())
        bind("Ctrl+Z", lambda: self.undo_last())
        bind("Ctrl+T", lambda: self.go_today())
        bind("Ctrl+F", lambda: (self.search.setFocus(), self.search.selectAll()))
        bind("Alt+Left", lambda: self.show_day(self.current.addDays(-1)))
        bind("Alt+Right", lambda: self.show_day(self.current.addDays(1)))

    def _build_tray(self):
        if self.selftest or not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self.tray = QSystemTrayIcon(self.windowIcon(), self)
        self.tray.setToolTip(T("app"))
        self.tray_menu = QMenu()
        act = self.tray_menu.addAction(T("tray_open"))
        act.triggered.connect(lambda *_: self.show_from_tray())
        act = self.tray_menu.addAction(T("tray_new"))
        act.triggered.connect(lambda *_: self.quick_note())
        self.tray_menu.addSeparator()
        act = self.tray_menu.addAction(T("tray_quit"))
        act.triggered.connect(lambda *_: self.quit_app())
        self.tray.setContextMenu(self.tray_menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    # -------------------------------------------------------------- тема
    def apply_theme(self, name, save=True):
        Theme.use(name)
        app = QApplication.instance()
        if not isinstance(app, QApplication):
            return
        app.setPalette(build_palette())
        app.setStyleSheet(QSS.substitute(
            {k: str(v) for k, v in Theme.colors.items()}))
        self.app_title.setStyleSheet(f"color: {Theme.colors['ink']};")
        self.calendar.apply_theme()
        self.theme_btn.setText(T("light_theme") if Theme.name == "dark"
                               else T("dark_theme"))
        for w in self.findChildren(QWidget):
            w.update()
        if save and self.cfg.get("theme") != Theme.name:
            self.cfg["theme"] = Theme.name
            save_config(self.cfg)
        if self.archive_panel.isVisible():
            self.archive_panel.refresh(self.store.peek(self.key())["archived"])

    def toggle_theme(self):
        self.apply_theme("light" if Theme.name == "dark" else "dark")

    def apply_settings(self, theme, lang):
        """Применяет сохранённые настройки; смена языка пересобирает окно."""
        self.board.restyle()
        self.apply_theme(theme)
        if lang != LANG:
            self.cfg["lang"] = lang
            save_config(self.cfg)
            set_language(lang)
            install_translator(lang)
            if self.on_rebuild:
                QTimer.singleShot(0, self.on_rebuild)
                return
        self.refresh_meta()

    # ------------------------------------------------------- дата и день
    def key(self):
        return self.current.toString("yyyy-MM-dd")

    def today_key(self):
        return self.today.toString("yyyy-MM-dd")

    def viewing_today(self):
        return self.current == self.today

    def go_today(self):
        self.show_day(self.today)

    def show_day(self, qdate, flush=True):
        if not qdate.isValid():
            return
        if flush:
            self._save_timer.stop()
            self.flush_and_save(refresh=False)
        self.current = qdate
        if self.store.materialize(self.key(), self.today_key(), self._avail()):
            self.store.save()
        self.board.load(self.store.peek(self.key())["active"])
        if self.calendar.selectedDate() != qdate:
            self.calendar.setSelectedDate(qdate)
        self._on_page_changed(self.calendar.yearShown(), self.calendar.monthShown())
        self.board_scroll.horizontalScrollBar().setValue(0)
        self.board_scroll.verticalScrollBar().setValue(0)
        self.refresh_meta()

    def _avail(self):
        return self.board.avail_width() if self._loaded else max(600, self.width() - 330)

    def _on_calendar_selection(self):
        d = self.calendar.selectedDate()
        if d != self.current:
            self.show_day(d)

    def _on_page_changed(self, year, month):
        self.month_label.setText(f"{MONTHS_NOM[LANG][month - 1]} {year}")

    def _tick(self):
        now = QDate.currentDate()
        if now != self.today:
            was_today = self.viewing_today()
            self.today = now
            self.ensure_plan_note()
            self.materialize_today()
            if was_today:
                self.show_day(now)
            self.refresh_meta()
        self.check_reminders()

    # ------------------------------------------------ обязательная заметка
    def ensure_plan_note(self):
        day = qdate_to_py(self.today)
        plan_days = list(self.cfg.get("plan_days") or [])
        if not plan_needed(day, plan_days):
            return False
        today_day = self.store.peek(self.today_key())
        if any(n.get("kind") == "plan" for n in today_day["active"] + today_day["archived"]):
            return False
        if self._loaded:
            self.flush()
        key = self.today_key()
        avail = (self.board.avail_width() if self._loaded
                 else max(600, self.width() - 330))
        self.store.add_plan_note(key, T("plan_text"),
                                 self.cfg.get("plan_time", DEFAULT_PLAN_TIME), avail)
        plan_days.append(day.isoformat())
        self.cfg["plan_days"] = plan_days[-40:]
        save_config(self.cfg)
        self.store.save()
        if self._loaded and self.viewing_today():
            self.reload_board()
        return True

    def materialize_today(self):
        if self._loaded:
            self.flush()
        if self.store.materialize(self.today_key(), self.today_key(), self._avail()):
            self.store.save()
            if self._loaded and self.viewing_today():
                self.reload_board()

    # ------------------------------------------------------ сохранение
    def flush(self):
        """Переносит состояние доски в хранилище."""
        if self._loaded:
            self.store.day(self.key())["active"] = self.board.items()

    def flush_and_save(self, refresh=True):
        if not self._loaded:
            return
        self.flush()
        self.store.save()
        if refresh:
            self.refresh_meta()

    def schedule_save(self):
        if self._loaded:
            self._save_timer.start()

    def board_changed(self):
        if not self._loaded:
            return
        self.flush()
        self._save_timer.start()
        self.refresh_meta()

    def reload_board(self):
        self.board.load(self.store.peek(self.key())["active"])

    # ------------------------------------------------- обновление подписей
    def refresh_meta(self):
        py = qdate_to_py(self.current)
        py_today = qdate_to_py(self.today)
        weekday = WEEKDAYS[LANG][py.weekday()].upper()
        delta = (py - py_today).days
        mark = {0: T("mark_today"), 1: T("mark_tomorrow"),
                -1: T("mark_yesterday")}.get(delta)
        self.weekday_label.setText(f"{weekday}  ·  {mark}" if mark else weekday)
        self.date_label.setText(day_month(py, py.year != py_today.year))
        self.today_btn.setEnabled(delta != 0)

        active = len(self.board.notes) if self._loaded else \
            len(self.store.peek(self.key())["active"])
        archived = len(self.store.peek(self.key())["archived"])
        parts = []
        if active:
            parts.append(count_text(active))
        if archived:
            parts.append(T("n_done", n=archived))
        self.stats_label.setText("  ·  ".join(parts) if parts else T("no_notes"))
        self.archive_btn.setText(f"{T('archive')}  {archived}" if archived
                                 else T("archive"))
        self.tidy_btn.setEnabled(active > 0)
        self.undo_btn.setEnabled(bool(self.undo.get(self.key())))
        self.carry_btn.setVisible(bool(self.store.overdue_keys(self.today_key())))

        self.calendar.updateCells()
        self.refresh_side_list()
        if self.archive_panel.isVisible():
            self.archive_panel.refresh(self.store.peek(self.key())["archived"])

    def _side_row(self, left, right, payload, hot=False, tip=None):
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, payload)
        item.setSizeHint(QSize(0, 34))
        if tip:
            item.setToolTip(tip)
        if payload is None:
            item.setFlags(Qt.ItemFlag.NoItemFlags)
        row = QWidget()
        row.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        lay = QHBoxLayout(row)
        lay.setContentsMargins(10, 0, 10, 0)
        lay.setSpacing(8)
        a = QLabel()
        a.setTextFormat(Qt.TextFormat.PlainText)
        if payload is None:
            a.setObjectName("Hint")
        b = QLabel(right)
        b.setObjectName("CountHot" if hot else "Count")
        width = 214 - (QFontMetrics(b.font()).horizontalAdvance(right) + 8 if right else 0)
        a.setText(QFontMetrics(a.font()).elidedText(left, Qt.TextElideMode.ElideRight, width))
        lay.addWidget(a, 1)
        lay.addWidget(b)
        self.side_list.addItem(item)
        self.side_list.setItemWidget(item, row)
        row.setAutoFillBackground(False)

    def refresh_side_list(self):
        self.side_list.clear()
        py_today = qdate_to_py(self.today)
        query = self.search.text().strip()
        if query:
            self._show_side_list(True)
            self.section.setText(T("found"))
            hits = self.store.search(query)
            if not hits:
                self._side_row(T("nothing_found"), "", None)
            for hit in hits:
                d = parse_key(hit["key"])
                text = " ".join(hit["text"].split())
                when = human_date(d, py_today)
                right = when + (T("archive_suffix") if hit["archived"] else "")
                self._side_row(text, right, hit, tip=hit["text"][:600])
            return

        # дни с заметками видны точками в календаре — отдельный список не нужен
        self._show_side_list(False)

    def _show_side_list(self, on):
        self.section.setVisible(on)
        self.side_list.setVisible(on)
        self.side_filler.setVisible(not on)

    def _on_side_item(self, item):
        payload = item.data(Qt.ItemDataRole.UserRole)
        if not payload:
            return
        d = QDate.fromString(payload["key"], "yyyy-MM-dd")
        self.show_day(d)
        if payload.get("archived"):
            self.archive_btn.setChecked(True)
            return
        self.focus_note(payload.get("id"))

    def focus_note(self, note_id):
        note = self.board.find_note(note_id) if note_id else None
        if note is not None:
            self.board.raise_note(note)
            self.board_scroll.ensureWidgetVisible(note, 24, 24)
            note.edit.setFocus()

    def set_status(self, text, ms=7000):
        self.status.setText(text)
        self._status_timer.stop()
        if ms:
            self._status_timer.start(ms)

    # ---------------------------------------------------------- заметки
    def new_note(self, x=None, y=None, text="", focus=True):
        if x is None or y is None:
            x, y = find_free_spot(self.board.rects(), NOTE_W, NOTE_H,
                                  self.board.avail_width())
        ci = len(self.board.notes) % 7
        data = {"id": str(uuid.uuid4()), "x": max(0, int(x)), "y": max(0, int(y)),
                "w": NOTE_W, "h": NOTE_H, "text": text, "ci": ci,
                "created": datetime.now().isoformat(timespec="seconds")}
        note = self.board.add_note(data, focus=focus)
        self.board_scroll.ensureWidgetVisible(note, 24, 24)
        return note

    def quick_note(self):
        self.show_from_tray()
        self.go_today()
        self.new_note()

    def _push_undo(self, entry):
        self.undo.setdefault(self.key(), []).append(entry)

    def complete_note(self, note):
        data = note.to_dict()
        archived = dict(data)
        archived["done_at"] = datetime.now().isoformat(timespec="seconds")
        self.store.day(self.key())["archived"].append(archived)
        self._push_undo({"type": "completed", "data": data})
        self.board.remove_note(note)

    def delete_note(self, note):
        if note.kind == "plan":
            return
        if note.rid:
            self.store.skip(note.rid, self.key())
        self._push_undo({"type": "deleted", "data": note.to_dict()})
        self.board.remove_note(note)

    def duplicate_note(self, note):
        data = note.to_dict()
        data["id"] = str(uuid.uuid4())
        data["x"] += 26
        data["y"] += 26
        data["created"] = datetime.now().isoformat(timespec="seconds")
        for k in ("source", "yandex_uid", "kind", "fired", "remind", "rid"):
            data.pop(k, None)
        self.board.add_note(data)

    def move_note_pick(self, note):
        dlg = MoveDialog(self, self.current)
        if dlg.exec() and dlg.result_date is not None:
            self.move_note(note, dlg.result_date)
        return dlg

    def move_note(self, note, target):
        tkey = target.toString("yyyy-MM-dd")
        if not target.isValid() or tkey == self.key():
            return
        data = note.to_dict()
        self._push_undo({"type": "moved", "data": dict(data), "to": tkey})
        data.pop("fired", None)
        if data.get("rid"):
            # перенесённый экземпляр становится обычной заметкой, а в этот день
            # повтор больше не появится
            self.store.skip(data.pop("rid"), self.key())
        tday = self.store.day(tkey)
        data["x"], data["y"] = find_free_spot(
            rects_of(tday["active"]), data["w"], data["h"], self.board.avail_width())
        tday["active"].append(data)
        self.board.remove_note(note)
        py = qdate_to_py(target)
        self.set_status(T("moved_to", d=human_date_inline(py, qdate_to_py(self.today))))

    def undo_last(self):
        stack = self.undo.get(self.key()) or []
        if not stack:
            return
        entry = stack.pop()
        data = dict(entry["data"])
        note_id = data.get("id")
        if entry["type"] == "completed":
            day = self.store.day(self.key())
            day["archived"] = [a for a in day["archived"] if a.get("id") != note_id]
        elif entry["type"] == "moved":
            tday = self.store.day(entry["to"])
            tday["active"] = [a for a in tday["active"] if a.get("id") != note_id]
        self.board.add_note(data)

    def restore_archived(self, note_id):
        day = self.store.day(self.key())
        for i, a in enumerate(day["archived"]):
            if a.get("id") == note_id:
                data = dict(day["archived"].pop(i))
                data.pop("done_at", None)
                self.board.add_note(data)
                return

    def delete_archived(self, note_id):
        day = self.store.day(self.key())
        day["archived"] = [a for a in day["archived"] if a.get("id") != note_id]
        self.board_changed()

    def carry_over(self, confirm=True):
        keys = self.store.overdue_keys(self.today_key())
        total = sum(self.store.counts(k)[0] for k in keys)
        if not total:
            return 0
        if confirm:
            answer = QMessageBox.question(
                self, T("app"), T("carry_q", n=total, w=word(total, "note_acc")))
            if answer != QMessageBox.StandardButton.Yes:
                return 0
        self._save_timer.stop()
        self.flush()
        moved = self.store.carry_overdue(self.today_key(), self.board.avail_width())
        self.store.save()
        self.reload_board()
        self.refresh_meta()
        self.set_status(T("carried", n=moved))
        return moved

    def _toggle_archive(self, on):
        self.archive_panel.setVisible(on)
        if on:
            self.archive_panel.refresh(self.store.peek(self.key())["archived"])

    def open_settings(self):
        SettingsDialog(self).exec()

    # ------------------------------------------------------- напоминания
    def edit_reminder(self, note):
        created = parse_dt(note.created)
        dlg = ReminderDialog(self, qdate_to_py(self.current), created, note.remind)
        if dlg.exec() and dlg.outcome == "ok":
            note.remind = dlg.remind
            note.fired = []
            note.update_reminder_view()
            self.board_changed()
        return dlg

    def edit_repeat(self, note):
        t = self.store.template(note.rid) if note.rid else None
        dlg = RepeatDialog(self, qdate_to_py(self.current), t["rule"] if t else None)
        if dlg.exec() and dlg.outcome == "ok":
            if dlg.rule is None:
                if note.rid:
                    self.store.remove_rule(note.rid)
                note.rid = None
            else:
                note.rid = self.store.set_rule(note.to_dict(), self.key(), dlg.rule)
            note.update_reminder_view()
            self.board_changed()
            self.store.save()
        return dlg

    def check_reminders(self, now=None):
        """Показывает уведомления, срок которых наступил. Возвращает их число."""
        now = now or datetime.now()
        tk = now.date().isoformat()
        if self._loaded:
            self.flush()
        shown = 0
        for data in list(self.store.day(tk)["active"]):
            due, snoozed = due_reminders(data, tk, now)
            if not due and not snoozed:
                continue
            fired = prune_fired(list(data.get("fired") or []) + due, tk)
            remind = dict(data.get("remind") or {})
            if snoozed:
                remind.pop("snooze", None)
            self._update_note_state(tk, data.get("id"), remind, fired)
            when = due[-1].split(" ")[1] if due else now.strftime("%H:%M")
            ci = data.get("ci") if isinstance(data.get("ci"), int) else 0
            self.popups.show(note_id=data.get("id"), day_key=tk,
                             text=data.get("text", ""), when=when, ci=ci,
                             palette=self.sticker_palette(), font=self.note_font())
            shown += 1
        if shown:
            self.store.save()
        return shown

    def _update_note_state(self, day_key, note_id, remind, fired):
        """Обновляет напоминание заметки и в хранилище, и на доске."""
        for d in self.store.day(day_key)["active"]:
            if d.get("id") == note_id:
                if remind and remind.get("times"):
                    d["remind"] = remind
                else:
                    d.pop("remind", None)
                d["fired"] = fired
        if self.key() == day_key:
            w = self.board.find_note(note_id)
            if w is not None:
                w.remind = remind if remind and remind.get("times") else None
                w.fired = fired
                w.update_reminder_view()

    def reminder_action(self, kind, note_id, day_key):
        self.flush()
        data = next((d for d in self.store.day(day_key)["active"]
                     if d.get("id") == note_id), None)
        if data is None:
            return
        if kind == "done":
            widget = self.board.find_note(note_id) if self.key() == day_key else None
            if widget is not None:
                self.complete_note(widget)
            else:
                day = self.store.day(day_key)
                day["active"] = [d for d in day["active"] if d.get("id") != note_id]
                done = dict(data)
                done["done_at"] = datetime.now().isoformat(timespec="seconds")
                day["archived"].append(done)
            self.store.save()
            self.refresh_meta()
        elif kind == "snooze":
            remind = dict(data.get("remind") or {"mode": "once", "times": []})
            remind["snooze"] = (datetime.now() + timedelta(minutes=SNOOZE_MINUTES)
                                ).isoformat(timespec="seconds")
            if not remind.get("times"):
                remind["times"] = [datetime.now().strftime("%H:%M")]
            self._update_note_state(day_key, note_id, remind,
                                    list(data.get("fired") or []))
            self.store.save()
        elif kind == "open":
            self.show_from_tray()
            self.show_day(QDate.fromString(day_key, "yyyy-MM-dd"))
            self.focus_note(note_id)

    # ----------------------------------------------- Яндекс.Календарь
    def sync_yandex(self):
        if self._sync_thread is not None:
            return
        username = self.cfg.get("username")
        password = self.cfg.get("password")
        if not username or not password:
            QMessageBox.information(self, T("yandex"), T("y_need_login"))
            self.open_settings()
            return

        self.set_status(T("y_loading"), 0)
        self.sync_btn.setEnabled(False)
        self._sync_key = self.key()
        day = qdate_to_py(self.current)

        self._sync_thread = QThread(self)
        self._sync_worker = YandexSyncWorker(username, password, day)
        self._sync_worker.moveToThread(self._sync_thread)
        self._sync_thread.started.connect(self._sync_worker.run)
        self._sync_worker.finished.connect(self._on_sync_finished)
        self._sync_worker.error.connect(self._on_sync_error)
        self._sync_worker.finished.connect(self._sync_thread.quit)
        self._sync_worker.error.connect(self._sync_thread.quit)
        self._sync_thread.finished.connect(self._sync_cleanup)
        self._sync_thread.start()

    def _on_sync_finished(self, events):
        try:
            self._save_timer.stop()
            self.flush()
            added = self.store.import_events(self._sync_key, events,
                                             self.board.avail_width())
            self.store.save()
            if self._sync_key == self.key():
                self.reload_board()
            self.refresh_meta()
            self.set_status(T("y_result", n=len(events), a=added))
        except Exception as e:
            traceback.print_exc()
            self._on_sync_error(str(e))

    def _on_sync_error(self, msg):
        self.set_status("")
        QMessageBox.warning(self, T("yandex"), T("y_fail", e=msg))

    def _sync_cleanup(self):
        if self._sync_worker is not None:
            self._sync_worker.deleteLater()
        if self._sync_thread is not None:
            self._sync_thread.deleteLater()
        self._sync_worker = None
        self._sync_thread = None
        self.sync_btn.setEnabled(True)

    # ----------------------------------------------------- окно и трей
    def _restore_geometry(self):
        if self.selftest:
            return
        raw = self.cfg.get("geometry")
        if raw:
            try:
                self.restoreGeometry(QByteArray.fromBase64(raw.encode("ascii")))
            except Exception:
                pass

    def _remember_geometry(self):
        if self.selftest:
            return
        try:
            self.cfg["geometry"] = bytes(
                self.saveGeometry().toBase64().data()).decode("ascii")
            save_config(self.cfg)
        except Exception:
            traceback.print_exc()

    def _on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger,
                      QSystemTrayIcon.ActivationReason.DoubleClick):
            if self.isVisible() and not self.isMinimized() and self.isActiveWindow():
                self.hide()
            else:
                self.show_from_tray()

    def show_from_tray(self):
        self._tick()
        if self.isMinimized():
            self.showNormal()
        else:
            self.show()
        self.raise_()
        self.activateWindow()

    def shutdown_for_rebuild(self):
        """Тихо закрывает окно перед пересборкой (смена языка)."""
        self._quitting = True
        self._clock.stop()
        self._save_timer.stop()
        self.flush_and_save(refresh=False)
        if self.tray is not None:
            self.tray.hide()
            self.tray.deleteLater()
            self.tray = None
        self.close()
        self.deleteLater()

    def quit_app(self):
        self._quitting = True
        self._save_timer.stop()
        self.flush_and_save(refresh=False)
        self._remember_geometry()
        self.popups.close_all()
        if self.tray is not None:
            self.tray.hide()
        if self._sync_thread is not None:
            self._sync_thread.quit()
            if not self._sync_thread.wait(1500):
                os._exit(0)  # сеть не отвечает — данные уже сохранены
        QApplication.quit()

    def closeEvent(self, e):
        self._save_timer.stop()
        self.flush_and_save(refresh=False)
        if self._quitting or self.selftest:
            e.accept()
            return
        if self.tray is None:
            e.accept()
            self.quit_app()
            return
        e.ignore()
        self._remember_geometry()
        self.hide()
        if not self.cfg.get("tray_notice_shown"):
            self.cfg["tray_notice_shown"] = True
            save_config(self.cfg)
            self.tray.showMessage(T("app"), T("tray_notice"),
                                  QSystemTrayIcon.MessageIcon.Information, 4000)


_TRANSLATOR = None


def install_translator(lang):
    """Подписи стандартных кнопок и меню Qt (Да/Нет, Копировать…)."""
    global _TRANSLATOR
    app = QApplication.instance()
    if app is None:
        return
    try:
        from PySide6.QtCore import QTranslator, QLibraryInfo
        if _TRANSLATOR is not None:
            app.removeTranslator(_TRANSLATOR)
            _TRANSLATOR = None
        QLocale.setDefault(current_qlocale())
        if lang == "ru":
            tr = QTranslator(app)
            path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
            if tr.load("qtbase_ru", path):
                app.installTranslator(tr)
                _TRANSLATOR = tr
    except Exception:
        traceback.print_exc()


def setup_app_style(app):
    app.setStyle("Fusion")
    font = QFont(ui_family())
    font.setPixelSize(13)
    app.setFont(font)


# ----------------------------- Самопроверка -----------------------------
def run_selftest(outdir):
    """Прогоняет интерфейс на пробных данных и сохраняет снимки окна."""
    global CONFIG_FILE
    os.makedirs(outdir, exist_ok=True)
    for name in os.listdir(outdir):
        if name.endswith(".png"):
            try:
                os.remove(os.path.join(outdir, name))
            except OSError:
                pass
    CONFIG_FILE = os.path.join(outdir, "config.json")
    report = []
    qt_messages = []
    err_path = os.path.join(outdir, "stderr.txt")
    old_err = sys.stderr
    sys.stderr = open(err_path, "w", encoding="utf-8", buffering=1)
    qInstallMessageHandler(lambda mode, ctx, msg: qt_messages.append(str(msg)))

    def step(name, fn):
        try:
            fn()
            report.append("OK    " + name)
        except Exception:
            report.append("FAIL  " + name + "\n" + traceback.format_exc())

    def check(cond, what):
        if not cond:
            raise AssertionError(what)

    today = pydate.today()
    morning_iso = datetime.now().replace(hour=9, minute=0, second=0,
                                         microsecond=0).isoformat(timespec="seconds")

    def k(delta):
        return (today + timedelta(days=delta)).isoformat()

    sample = {
        k(0): {"active": [
            {"id": "a1", "x": 40, "y": 30, "text": "Позвонить в деканат", "color": "#FFF9A6",
             "created": morning_iso,
             "remind": {"mode": "twice", "times": ["10:00", "17:00"], "since": morning_iso}},
            {"id": "a2", "x": 310, "y": 60, "text": "Купить молоко и хлеб\n— кефир\n— яблоки",
             "color": "#FFD6A5", "created": morning_iso},
            {"id": "a3", "x": 580, "y": 40, "text": "10:00  Семинар\nауд. 304",
             "color": "#BDE0FE", "source": "yandex", "yandex_uid": "u-1"},
            {"id": "a4", "x": 40, "y": 290, "text": "Список литературы к главе 2",
             "ci": 6, "created": morning_iso},
            {"id": "a5", "x": 310, "y": 300, "text": "Подарок маме", "ci": 4,
             "created": morning_iso},
        ], "archived": [
            {"id": "z1", "x": 10, "y": 10, "text": "Сдать отчёт", "color": "#C8F7C5"}]},
        k(-2): {"active": [
            {"id": "b1", "x": 40, "y": 30, "text": "Старая задача", "color": "#F8C8DC"}],
            "archived": []},
        k(3): {"active": [
            {"id": "c1", "x": 40, "y": 30, "text": "Билеты", "color": "#E0D3F5"}],
            "archived": []},
    }
    data_path = os.path.join(outdir, "data.json")
    save_json_atomic(data_path, sample)

    set_language("ru")
    app = QApplication(sys.argv)
    bundled = load_bundled_fonts()
    setup_app_style(app)
    install_translator("ru")

    store = Store(data_path)
    cfg: dict = {"palette": "kraft"}
    box: dict = {}
    popups = PopupManager(lambda: box.get("win"))
    popups.offscreen = True

    def shot(widget, name):
        app.processEvents()
        if not widget.grab().save(os.path.join(outdir, name)):
            raise RuntimeError("не удалось сохранить " + name)

    def make_window():
        win = MainWindow(store, cfg, popups, selftest=True)
        win.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
        win.resize(1360, 820)
        win.show()
        app.processEvents()
        box["win"] = win
        return win

    def offscreen_dialog(dlg, name):
        dlg.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
        dlg.show()
        shot(dlg, name)
        dlg.reject()

    step("окно создано", make_window)
    win = box.get("win")
    if win is not None:
        def plan_created():
            plans = [d for d in store.peek(win.today_key())["active"]
                     if d.get("kind") == "plan"]
            if today.weekday() == 5:
                check(not plans, "в субботу обязательной заметки быть не должно")
            else:
                check(len(plans) == 1, f"обязательных заметок: {len(plans)}")
                check(win.ensure_plan_note() is False, "повторное создание")
        step("обязательная заметка", plan_created)
        step("снимок: главное окно", lambda: shot(win, "01_main.png"))

        def hover_shot():
            note = win.board.find_note("a1")
            note._set_hover(True)
            shot(win.board_scroll, "02_board_hover.png")
            note._set_hover(False)
        step("снимок: наведение на заметку", hover_shot)

        def menu_shot():
            menu = win.board.find_note("a2").build_menu()
            menu.ensurePolished()
            menu.resize(menu.sizeHint())
            shot(menu, "03_menu.png")
        step("меню заметки", menu_shot)

        def move_dialog():
            dlg = MoveDialog(win, win.current)
            check(dlg.calendar.selectedDate() == win.current.addDays(1),
                  "по умолчанию — завтра")
            offscreen_dialog(dlg, "04_move_dialog.png")
        step("диалог переноса", move_dialog)

        def move_to_date():
            target = win.today.addDays(5)
            tkey = target.toString("yyyy-MM-dd")
            win.move_note(win.board.find_note("a2"), target)
            moved = [d for d in store.peek(tkey)["active"] if d.get("id") == "a2"]
            check(len(moved) == 1, "заметка не перенесена")
            check(win.board.find_note("a2") is None, "заметка осталась на доске")
            win.undo_last()
            check(win.board.find_note("a2") is not None, "отмена переноса")
            check(not store.peek(tkey)["active"], "остаток после отмены")
        step("перенос на выбранный день и отмена", move_to_date)

        def repeat():
            note = win.board.find_note("a5")
            dlg = RepeatDialog(win, today, None)
            check(dlg.r_none.isChecked(), "по умолчанию — не повторять")
            offscreen_dialog(dlg, "05b_repeat_dialog.png")
            rid = store.set_rule(note.to_dict(), win.key(), {"kind": "days", "days": [0, 2, 4]})
            note.rid = rid
            note.update_reminder_view()
            check(not note.rep_label.isHidden(), "значок повтора не виден")
            shot(note, "05c_note_repeat.png")
            win.board_changed()
            made = []
            for i in range(1, 8):
                d = win.today.addDays(i)
                win.show_day(d)
                if win.board.notes and any(n.rid == rid for n in win.board.notes):
                    made.append(qdate_to_py(d).weekday())
            check(sorted(made) == [0, 2, 4], f"повтор по дням: {made}")
            # удалили экземпляр — в этот день он больше не появится
            d = next(win.today.addDays(i) for i in range(1, 8)
                     if qdate_to_py(win.today.addDays(i)).weekday() == 2)
            win.show_day(d)
            inst = next(n for n in win.board.notes if n.rid == rid)
            win.delete_note(inst)
            win.show_day(win.today)
            win.show_day(d)
            check(not any(n.rid == rid for n in win.board.notes), "удалённый повтор вернулся")
            win.go_today()
            note = win.board.find_note("a5")
            store.remove_rule(note.rid)
            note.rid = None
            note.update_reminder_view()
            win.board_changed()
        step("повтор по дням недели", repeat)

        def reminder_dialog():
            note = win.board.find_note("a2")
            dlg = ReminderDialog(win, today, parse_dt(note.created), note.remind)
            check(dlg.r_twice.isChecked(), "до 12:00 — дважды в день")
            offscreen_dialog(dlg, "05_reminder_dialog.png")
            late = datetime.now().replace(hour=14, minute=0)
            dlg2 = ReminderDialog(win, today, late, None)
            check(dlg2.r_once.isChecked(), "после 12:00 — одно напоминание")
            dlg2.reject()
        step("диалог напоминания", reminder_dialog)

        def fire_reminder():
            at = datetime.now().replace(hour=10, minute=5, second=0, microsecond=0)
            n = win.check_reminders(at)
            check(n >= 1, f"напоминаний показано: {n}")
            check(win.check_reminders(at) == 0, "повторный показ того же напоминания")
            note = win.board.find_note("a1")
            check(note is not None and any(f.endswith("10:00") for f in note.fired),
                  "отметка о показе")
        step("срабатывание напоминания", fire_reminder)

        def popup_shot():
            check(bool(popups.popups), "уведомление не создано")
            shot(popups.popups[0], "06_popup.png")
        step("снимок: уведомление", popup_shot)

        def snooze():
            popup = popups.popups[0]
            note_id = popup.note_id
            popups.action("snooze", popup)
            note = win.board.find_note(note_id)
            check(note is not None and note.remind is not None
                  and bool(note.remind.get("snooze")), "отложено")
            later = datetime.now() + timedelta(minutes=SNOOZE_MINUTES + 1)
            if later.date() == today:
                check(win.check_reminders(later) >= 1, "отложенное напоминание")
            popups.close_all()
        step("отложить напоминание", snooze)

        def done_from_popup():
            p = popups.show(note_id="a5", day_key=win.today_key(), text="Подарок маме",
                            when="17:00", ci=4, palette=win.sticker_palette(), font=win.note_font())
            popups.action("done", p)
            check(win.board.find_note("a5") is None, "заметка не выполнена из уведомления")
            check(any(a.get("id") == "a5" for a in store.peek(win.today_key())["archived"]),
                  "нет в архиве")
            win.undo_last()
            check(win.board.find_note("a5") is not None, "отмена")
        step("«готово» из уведомления", done_from_popup)

        def settings():
            dlg = SettingsDialog(win)
            dlg.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
            dlg.show()
            app.processEvents()
            shot(dlg, "07_settings.png")
            fams = [dlg.font_box.itemData(i) for i in range(dlg.font_box.count())]
            check("Georgia" in fams and fams[-1] == OTHER_FONT, f"список шрифтов: {fams}")
            check(dlg.font_full.isHidden(), "полный список виден без «Другой…»")
            dlg.font_box.setCurrentIndex(dlg.font_box.findData("Georgia"))
            check(dlg.chosen_font()[0] == "Georgia", "выбор Georgia")
            dlg.font_box.setCurrentIndex(dlg.font_box.count() - 1)
            check(not dlg.font_full.isHidden(), "«Другой…» не показал полный список")
            check(bool(dlg.chosen_font()[0]), "шрифт из полного списка")
            report.append("      шрифтов в коротком списке: "
                          + str(sum(1 for f in fams if f and f != OTHER_FONT)))
            # как выглядит раскрытый список (рисуем его отдельно, без всплывающего окна)
            view = QListView()
            view.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
            view.setModel(dlg.font_box.model())
            view.setStyleSheet("QListView { background: %s; color: %s; border: 1px solid %s; }"
                               % (Theme.colors["surface"], Theme.colors["ink"],
                                  Theme.colors["line"]))
            view.resize(300, view.sizeHintForRow(1) * dlg.font_box.count() + 30)
            view.show()
            shot(view, "07b_font_list.png")
            view.close()
            dlg.reject()
        step("настройки", settings)

        step("выполнено", lambda: win.complete_note(win.board.find_note("a4")))
        step("архив открыт", lambda: win.archive_btn.setChecked(True))
        step("снимок: архив", lambda: shot(win, "08_archive.png"))
        step("закрыть архив", lambda: win.archive_btn.setChecked(False))
        step("список дней скрыт", lambda: check(win.side_list.isHidden(), "список виден"))
        step("поиск", lambda: win.search.setText("молоко"))
        step("снимок: поиск", lambda: shot(win, "09_search.png"))
        step("сброс поиска", lambda: win.search.setText(""))
        step("пустой день", lambda: win.show_day(win.today.addDays(10)))
        step("снимок: пустой день", lambda: shot(win, "10_empty.png"))
        step("сегодня", lambda: win.go_today())

        def palette_font():
            cfg["palette"] = "classic"
            cfg["note_font"] = "Georgia"
            cfg["note_font_size"] = 15
            win.board.restyle()
            shot(win.board_scroll, "11_palette_classic.png")
            cfg["palette"] = "nature"
            win.board.restyle()
            shot(win.board_scroll, "12_palette_nature.png")
            cfg["palette"] = "kraft"
            cfg.pop("note_font")
            cfg.pop("note_font_size")
            win.board.restyle()
        step("палитры и шрифт", palette_font)
        step("тёмная тема", lambda: win.apply_theme("dark", save=False))
        step("снимок: тёмная тема", lambda: shot(win, "13_dark.png"))
        step("светлая тема", lambda: win.apply_theme("light", save=False))

        def english():
            set_language("en")
            install_translator("en")
            win.flush_and_save()
            box["win"] = None
            win.close()
            win2 = make_window()
            shot(win2, "14_english.png")
            dlg = SettingsDialog(win2)
            dlg.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
            dlg.show()
            app.processEvents()
            shot(dlg, "15_settings_en.png")
            dlg.reject()
            p = popups.show(note_id="a1", day_key=win2.today_key(),
                            text="Call the dean's office", when="17:00", ci=4,
                            palette="kraft", font=win2.note_font())
            shot(p, "16_popup_en.png")
            popups.close_all()
            set_language("ru")
            install_translator("ru")
        step("английский интерфейс", english)

        def ical():
            import icalendar
            src = ("BEGIN:VCALENDAR\r\nVERSION:2.0\r\nBEGIN:VEVENT\r\nUID:t-1\r\n"
                   "SUMMARY:Встреча\r\nDTSTART:20261012T070000Z\r\n"
                   "DTEND:20261012T080000Z\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n")

            class Ev:
                icalendar_instance = icalendar.Calendar.from_ical(src)
            got = parse_ical_event(Ev())
            check(bool(got) and got["uid"] == "t-1", f"неожиданный результат: {got!r}")
        step("разбор события календаря", ical)

        def fonts():
            report.append(f"      система: {sys.platform}, Qt: {QGuiApplication.platformName()}, "
                          f"встроенные шрифты: {', '.join(bundled) or 'нет'}")
            report.append("      шрифт интерфейса: " + ui_family()
                          + ", шрифт заголовка: " + pick_family(SCRIPT_FONTS)
                          + ", шрифт заметок: " + pick_family(NOTE_FONTS)
                          + ", с засечками: " + pick_family(SERIF_FONTS))
        step("шрифты", fonts)

        def close_last():
            w = box.get("win")
            if w is not None:
                w.flush_and_save()
                w.close()
        step("закрытие", close_last)

    app.processEvents()
    sys.stderr.flush()
    sys.stderr = old_err
    try:
        with open(err_path, "r", encoding="utf-8") as f:
            errors = f.read().strip()
    except Exception:
        errors = ""
    failed = sum(1 for line in report if line.startswith("FAIL"))
    lines = [f"Заметки {APP_VERSION} — самопроверка",
             f"Python {sys.version.split()[0]}, {sys.executable}",
             f"Время: {datetime.now().isoformat(timespec='seconds')}",
             f"Шагов: {len(report)}, ошибок: {failed}", ""] + report
    lines += ["", "--- сообщения Qt ---"] + (qt_messages[:60] or ["(нет)"])
    lines += ["", "--- stderr ---", errors[-6000:] or "(пусто)"]
    with open(os.path.join(outdir, "report.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return 1 if (failed or errors) else 0


# -------------------------------- Запуск --------------------------------
def backup_once(cfg):
    """Перед первым запуском новой версии сохраняет копию заметок."""
    if cfg.get("v3_backup_done"):
        return
    try:
        if os.path.exists(DATA_FILE):
            shutil.copy2(DATA_FILE, DATA_FILE + ".v2-backup")
    except Exception:
        traceback.print_exc()
        return
    cfg["v3_backup_done"] = True
    save_config(cfg)


def run_build():
    """Собирает Заметки в exe (PyInstaller) и проверяет собранную программу.

    Пишет ход сборки в build.log рядом с программой. Результат:
    dist/Notes/Notes.exe и архив dist/Notes-windows.zip.
    """
    log_path = os.path.join(APP_DIR, "build.log")
    flags = 0x08000000 if IS_WIN else 0
    exe_dir = os.path.dirname(sys.executable)
    py = os.path.join(exe_dir, "python.exe") if IS_WIN else sys.executable
    if not os.path.exists(py):
        py = sys.executable
    dist = os.path.join(APP_DIR, "dist")
    work = os.path.join(APP_DIR, "build_tmp")
    with open(log_path, "w", encoding="utf-8") as log:
        def run(cmd, env=None, timeout=1500):
            log.write("\n> " + " ".join(cmd) + "\n")
            log.flush()
            try:
                r = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, env=env,
                                   cwd=APP_DIR, creationflags=flags, timeout=timeout)
                code = r.returncode
            except Exception as e:
                log.write(f"ошибка запуска: {e}\n")
                code = -1
            log.write(f"[код завершения {code}]\n")
            log.flush()
            return code

        log.write(f"Сборка Заметок {APP_VERSION}: {datetime.now().isoformat(timespec='seconds')}\n")
        if run([py, "-c", "import PyInstaller; print(PyInstaller.__version__)"]) != 0:
            pip = [py, "-m", "pip", "install", "--disable-pip-version-check", "pyinstaller"]
            if run(pip) != 0:
                # системный прокси Windows не отвечает — пробуем напрямую
                env = dict(os.environ, NO_PROXY="*", no_proxy="*")
                for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
                    env.pop(k, None)
                if run(pip, env=env) != 0:
                    log.write("BUILD FAILED: не удалось установить PyInstaller\n")
                    return 1
        cmd = [py, "-m", "PyInstaller", "--noconfirm", "--clean", "--windowed",
               "--name", "Notes", "--distpath", dist, "--workpath", work,
               "--specpath", work]
        icon = _png_icon() if IS_MAC else ICON_FILE
        if os.path.exists(icon):
            cmd += ["--icon", icon]
        for extra in (ICON_FILE, os.path.join(APP_DIR, "notes.png")):
            if os.path.exists(extra):
                cmd += ["--add-data", f"{extra}{os.pathsep}."]
        if os.path.isdir(os.path.join(APP_DIR, "fonts")):
            cmd += ["--add-data", f"{os.path.join(APP_DIR, 'fonts')}{os.pathsep}fonts"]
        for mod in ("tkinter", "tensorflow", "keras", "matplotlib", "numpy", "pandas",
                    "scipy", "PIL", "IPython", "notebook", "pytest"):
            cmd += ["--exclude-module", mod]
        cmd.append(os.path.abspath(__file__))
        if run(cmd) != 0:
            log.write("BUILD FAILED: PyInstaller завершился с ошибкой\n")
            return 1
        exe = (os.path.join(dist, "Notes", "Notes.exe") if IS_WIN else
               os.path.join(dist, "Notes.app", "Contents", "MacOS", "Notes") if IS_MAC else
               os.path.join(dist, "Notes", "Notes"))
        if not os.path.exists(exe):
            log.write("BUILD FAILED: exe не найден\n")
            return 1
        try:
            archive = shutil.make_archive(os.path.join(dist, "Notes-windows"), "zip",
                                          dist, "Notes")
            log.write(f"архив: {archive}\n")
        except Exception as e:
            log.write(f"архив не создан: {e}\n")
        code = run([exe, "--selftest", os.path.join(APP_DIR, "selftest_exe")], timeout=300)
        log.write("BUILD OK\n" if code == 0 else "BUILD OK, но самопроверка exe с ошибками\n")
    return 0


def spawn_selftest():
    """Если рядом лежит selftest.flag — в фоне запускает самопроверку."""
    flag = os.path.join(APP_DIR, "selftest.flag")
    if not os.path.exists(flag):
        return
    try:
        os.remove(flag)
        out = os.path.join(APP_DIR, "selftest")
        cmd = ([sys.executable, "--selftest", out] if FROZEN
               else [sys.executable, os.path.abspath(__file__), "--selftest", out])
        subprocess.Popen(cmd, creationflags=0x08000000 if sys.platform == "win32" else 0)
    except Exception:
        traceback.print_exc()


def main():
    args = sys.argv[1:]

    build_flag = os.path.join(APP_DIR, "build.flag")
    if "--build" in args or ("--selftest" in args and not FROZEN
                             and os.path.exists(build_flag)):
        try:
            os.remove(build_flag)
        except OSError:
            pass
        sys.exit(run_build())

    if "--selftest" in args:
        i = args.index("--selftest")
        outdir = args[i + 1] if len(args) > i + 1 else os.path.join(APP_DIR, "selftest")
        sys.exit(run_selftest(outdir))

    cfg = load_config()
    set_language(cfg.get("lang", "ru"))

    if "--make-shortcut" in args:
        ok, text = create_desktop_shortcut()
        print(text)
        sys.exit(0 if ok else 1)

    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "Stickies.Notes.3")
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setApplicationName("Stickies")
    app.setApplicationDisplayName(T("app"))
    app.setDesktopFileName("notes-paper")
    app.setQuitOnLastWindowClosed(False)
    load_bundled_fonts()
    setup_app_style(app)
    app.setWindowIcon(make_app_icon())
    install_translator(LANG)
    # Самопроверка по файлу-флажку selftest.flag рядом с программой: в фоне и
    # без окон прогоняется копия интерфейса на пробных данных, отчёт и снимки —
    # в папке selftest. Заметки пользователя не затрагиваются.
    spawn_selftest()

    # второй запуск просто показывает уже работающее окно
    server_name = "stickies-notes-" + hashlib.md5(HOME.encode("utf-8")).hexdigest()[:12]
    probe = QLocalSocket()
    probe.connectToServer(server_name)
    if probe.waitForConnected(400):
        if "--tray" not in args:
            probe.write(b"show")
            probe.flush()
            probe.waitForBytesWritten(400)
        probe.disconnectFromServer()
        sys.exit(0)
    QLocalServer.removeServer(server_name)
    server = QLocalServer()
    server.listen(server_name)

    backup_once(cfg)
    store = Store()
    holder = {}
    popups = PopupManager(lambda: holder.get("win"))

    def rebuild():
        old = holder.get("win")
        geo = old.saveGeometry() if old is not None else None
        visible = old.isVisible() if old is not None else True
        if old is not None:
            old.shutdown_for_rebuild()
        app.setApplicationDisplayName(T("app"))
        win = MainWindow(store, cfg, popups, on_rebuild=rebuild)
        if geo is not None:
            win.restoreGeometry(geo)
        holder["win"] = win
        if visible:
            win.show()

    holder["win"] = MainWindow(store, cfg, popups, on_rebuild=rebuild)

    def on_second_launch():
        conn = server.nextPendingConnection()
        if conn is not None:
            conn.disconnectFromServer()
        holder["win"].show_from_tray()

    def on_quit():
        w = holder.get("win")
        if w is not None:
            w._save_timer.stop()
            w.flush_and_save(refresh=False)

    server.newConnection.connect(on_second_launch)
    app.aboutToQuit.connect(on_quit)

    if "--tray" not in args or holder["win"].tray is None:
        holder["win"].show()

    if not FROZEN:
        watcher = QTimer(app)
        watcher.setInterval(5000)
        watcher.timeout.connect(spawn_selftest)
        watcher.start()

    sys.exit(app.exec())


def run():
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        err = traceback.format_exc()
        print(err)
        fatal(T("app") + ": " + err[-1500:])


if __name__ == "__main__":
    run()
