from main import bot, dp, table
from aiogram import types


# a handler for admins to confirm or deny book requests and make changes in google sheets
@dp.callback_query_handler(lambda callback: callback.data.split()[0] == 'book')
async def response_to_book(callback: types.CallbackQuery):
    answer, rng = callback.data.split()[1:]
    row = table.get(rng)
    if answer == 'confirm':
        row[0][-1] = 'Согласовано'
    elif answer == 'deny':
        row[0][-1] = 'Отказано'
    table.update(row, rng)
    text = 'Вы ответили на заявку, данные в таблице изменены'
    await callback.message.edit_text(text)
