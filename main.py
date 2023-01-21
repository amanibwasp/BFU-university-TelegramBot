import os
from datetime import time
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import BOT_TOKEN, SPREADSHEAT_ID  # you need create config.py
# file and nest inside ur
# BOT_TOKEN and SPREADSHEET_ID for interacting with Google sheets
from utils.table import Table

bot = Bot(BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
table = Table(SPREADSHEAT_ID)
table.set_sheet('Заявки') #Title of the sheet you connect with the bot

if __name__ == '__main__':
    from handlers import *

    executor.start_polling(dp, skip_updates=True)
