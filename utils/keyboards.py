import datetime

from aiogram.types import *
from main import dp
from utils.states import *
from config import audiences


def start_keyboard():
    kb = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    kb.add(
        KeyboardButton(text="Забронировать аудиторию"))
    return kb


def choose_auditorium_kb():
    kb = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for a in audiences:
        kb.add(a)
    return kb


def choose_time_to_start(can_book=True):
    kb = InlineKeyboardMarkup(resize_keyboard=True, row_width=4)
    kb.row(InlineKeyboardButton('⏫', callback_data='update_time_to_start 3 0'),
           InlineKeyboardButton('🔼', callback_data='update_time_to_start 1 0'), \
           InlineKeyboardButton('⏫', callback_data='update_time_to_start 0 15'),
           InlineKeyboardButton('🔼', callback_data='update_time_to_start 0 5')) \
        .row(InlineKeyboardButton('Часы', callback_data='IGNORE'),
             InlineKeyboardButton('Минуты', callback_data='IGNORE')) \
        .row(InlineKeyboardButton('⏬', callback_data='update_time_to_start -3 0'),
             InlineKeyboardButton('🔽', callback_data='update_time_to_start -1 0'), \
             InlineKeyboardButton('⏬', callback_data='update_time_to_start 0 -15'),
             InlineKeyboardButton('🔽', callback_data='update_time_to_start 0 -5'))
    if can_book:
        kb.insert(InlineKeyboardButton('✅', callback_data='accept_time_to_start'))
    return kb


def choose_duration(can_book=True):
    kb = InlineKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.row(InlineKeyboardButton('🔼', callback_data='update_duration 1 0'), \
           InlineKeyboardButton('🔼', callback_data='update_duration 0 5')) \
        .row(InlineKeyboardButton('Часы', callback_data='IGNORE'),
             InlineKeyboardButton('Минуты', callback_data='IGNORE')) \
        .row(InlineKeyboardButton('🔽', callback_data='update_duration -1 0'),
             InlineKeyboardButton('🔽', callback_data='update_duration 0 -5'))
    if can_book:
        kb.insert(InlineKeyboardButton('✅', callback_data='accept_duration'))
    return kb


# работает с datetime.datetime и datetime.timedelta
def beauty_time(t):
    if isinstance(t, datetime.datetime):
        with_digits = f'{str(t.hour).zfill(2)}:{str(t.minute).zfill(2)}'
    elif isinstance(t, datetime.timedelta):
        with_digits = f'{str(t.seconds // 3600).zfill(2)}:{str((t.seconds % 3600) // 60).zfill(2)}'
    return with_digits
