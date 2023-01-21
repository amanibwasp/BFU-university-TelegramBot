from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types

class FSMBook(StatesGroup):
    auditorium = State()
    date = State()
    start = State()
    finish = State()
    phone = State()

