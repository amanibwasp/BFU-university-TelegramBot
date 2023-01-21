import asyncio
import datetime
import pytz

from main import bot, dp, table
from config import TIME_OPEN, TIME_CLOSE, ADMINS, ALERT_TEXT  # TIME_OPEN, TIME_CLOSE - depends on ur schedule
# ADMINS - a list of admin's IDs.

from utils.keyboards import *
from utils.functions import *
from aiogram.dispatcher import FSMContext
from aiogram_calendar import simple_cal_callback, SimpleCalendar


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    neon = open('img/neon.jpg', 'rb')
    text = '''
<b>Привет! Я бот Студхауса БФУ им. И. Канта</b> 👻

<i>Студхаус БФУ им. И. Канта - это комплекс студенческих пространств Университета</i>
Здесь проводяться мастер-классы, творческие встречи, встречи студенческих сообществ и главные студенческие события БФУ им. И. Канта.
    '''
    await bot.send_photo(message.from_user.id, photo=neon,
                         caption=text,
                         reply_markup=start_keyboard())


@dp.message_handler(text='Забронировать аудиторию', state=None)
async def book_auditorium(message: types.Message):
    text = '''
Выберите аудиторию из списка

📌 список аудиторий можно листать вниз
    '''
    await bot.send_message(message.from_user.id, text, reply_markup=choose_auditorium_kb())
    await FSMBook.auditorium.set()


@dp.message_handler(state=FSMBook.auditorium)
async def book_auditorium_answer(message: types.Message, state: FSMContext):
    if message.text in audiences:
        await state.reset_state(with_data=False)
        await bot.send_message(message.from_user.id, f'Выбранная аудитория: {message.text}',
                               reply_markup=ReplyKeyboardRemove())
        await message.delete()
        await state.update_data(dict(auditorium=message.text))
        await bot.send_message(message.from_user.id, 'Теперь выберите дату бронирования:',
                               reply_markup=await SimpleCalendar().start_calendar())
    else:
        await bot.send_message(message.from_user.id,
                               f'Выбранная аудитория {message.text} недоступна для бронирования или не существует. Выберите, пожалуйста, другую аудиторию',
                               reply_markup=choose_auditorium_kb())


@dp.callback_query_handler(simple_cal_callback.filter())
async def process_simple_calendar(callback: types.CallbackQuery, callback_data: dict,
                                  state: FSMContext):
    data = await state.get_data()
    is_ready, date = await SimpleCalendar().process_selection(callback, callback_data)

    if is_ready:
        await callback.message.edit_text(f'Выбранная дата: {date.date()}')

        time_to_start = datetime.datetime.combine(date, datetime.time(hour=12, minute=0))
        await state.update_data(dict(
            time_to_start=time_to_start,
            duration=datetime.timedelta(hours=0, minutes=5)))
        text = '''
<b>Теперь укажите время начала бронирования:</b>
    
Сейчас указано: 12:00
            '''

        can_book = can_i_book(data['auditorium'], time_to_start,
                              datetime.timedelta(minutes=5), table.get())
        if not can_book:
            text += f'\n{ALERT_TEXT}'
        await bot.send_message(callback.from_user.id,
                               text,
                               reply_markup=choose_time_to_start(can_book=can_book),
                               parse_mode='HTML')


@dp.callback_query_handler(lambda callback: callback.data.split()[0] == 'update_time_to_start')
async def update_time_to_start(callback: types.CallbackQuery, state: FSMContext):
    ex_text = callback.message.text
    ex_kb = callback.message.reply_markup

    text = 'Время записи: {}'

    hours, minutes = map(int, callback.data.split()[1:])
    data = await state.get_data()
    time_to_start = data['time_to_start']
    new_time_to_start = time_to_start + datetime.timedelta(hours=hours, minutes=minutes)
    if TIME_OPEN <= new_time_to_start.time() <= TIME_CLOSE:
        await state.update_data(dict(time_to_start=new_time_to_start))

        can_book = can_i_book(data['auditorium'], new_time_to_start,
                              datetime.timedelta(minutes=5), table.get())
        text = text.format(beauty_time(new_time_to_start))
        if not can_book:
            text += f'\n{ALERT_TEXT}'

        await callback.message.edit_text(
            text=text.format(beauty_time(new_time_to_start)),
            reply_markup=choose_time_to_start(can_book=can_book),
            parse_mode='HTML')
    else:
        await callback.message.edit_text(
            '❌ <b>Студхаус работает с 9:00 до 21:30</b>\n\nВыберите другое время начала')
        await asyncio.sleep(1)
        await callback.message.edit_text(ex_text, reply_markup=ex_kb)


@dp.callback_query_handler(text='accept_time_to_start')
async def accept_time_to_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()

    data = await state.get_data()
    time_to_start = data['time_to_start']

    await bot.send_message(callback.from_user.id,
                           f'Выбранное время начала: {beauty_time(time_to_start)}')

    text = '''
<b>Теперь нужно выбрать, на сколько вы хотите забронировать аудиторию:</b>

сейчас аудитория будет забронирована на 00:05
    '''
    await bot.send_message(callback.from_user.id, text, reply_markup=choose_duration())


@dp.callback_query_handler(lambda callback: callback.data.split()[0] == 'update_duration')
async def update_duration(callback: types.CallbackQuery, state: FSMContext):
    ex_text = callback.message.text
    ex_kb = callback.message.reply_markup

    text = 'сейчас аудитория будет забронирована на {}'

    hours, minutes = map(int, callback.data.split()[1:])
    data = await state.get_data()
    duration = data['duration']
    new_duration = duration + datetime.timedelta(hours=hours, minutes=minutes)
    min_duration = 5 * 60
    if new_duration.total_seconds() >= min_duration and TIME_OPEN <= (
            data['time_to_start'] + new_duration).time() <= TIME_CLOSE:
        can_book = can_i_book(data['auditorium'], data['time_to_start'], new_duration, table.get())
        text = text.format(beauty_time(new_duration))
        if not can_book:
            text += f'\n{ALERT_TEXT}'
        await state.update_data(dict(duration=new_duration))
        await callback.message.edit_text(
            text=text,
            reply_markup=choose_duration(can_book=can_book))
    else:
        if new_duration.total_seconds() < min_duration:
            await callback.message.edit_text(
                '❌ <b>Ошибка, меньше чем на 5 минут, забронировать нельзя</b>')
        else:
            await callback.message.edit_text(
                '❌ <b>Студхаус работает с 9:00 до 21:30</b>\n\nВыберите другое время')

        await asyncio.sleep(1)
        await callback.message.edit_text(ex_text, reply_markup=ex_kb)


@dp.callback_query_handler(text='accept_duration')
async def accept_duration(callback: types.CallbackQuery, state: FSMContext):
    await FSMBook.phone.set()
    data = await state.get_data()
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.add(KeyboardButton('Поделиться контактами', request_contact=True))
    await callback.message.edit_text(
        f'Аудитория будет забронирована на: {beauty_time(data["duration"])}')
    await bot.send_message(callback.from_user.id, 'Теперь нам нужен ваш номер телефона',
                           reply_markup=kb)


@dp.message_handler(content_types=ContentType.CONTACT, state=FSMBook.phone)
async def get_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.reset_state(with_data=True)

    phone = message.contact.phone_number
    time_now = datetime_kld()
    time_to_start = data['time_to_start']
    duration = data['duration']
    auditorium = data['auditorium']

    if not can_i_book(auditorium, time_to_start, duration, table.get()):
        await message.answer(
            '<b>❌ В результате попытки брони произошла ошибка, попробуйте ещё раз</b>',
            reply_markup=start_keyboard())
        return

    await bot.send_message(message.from_user.id, '🎉 <b>Спасибо, мы Вам скоро перезвоним!</b>',
                           reply_markup=start_keyboard())
    await state.reset_state(with_data=False)

    row = table.append_row(str(time_now).split('.')[0],
                           auditorium,
                           str(time_to_start),
                           str(time_to_start + duration),
                           phone,
                           'На рассмотрении')

    updated_range = row['updates']['updatedRange'].split('!')[1]

    text = f'''
👉 <b>Новая заявка</b> 

Аудитория: {auditorium}
Дата: {time_to_start.date()}
Время начала бронирования: {time_to_start.time()}
Время конца бронирвания: {(time_to_start + duration).time()}
Телефон: {phone}

<u>Подтвердить бронь?</u>
    '''
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton(text='✅', callback_data=f'book confirm {updated_range}'),
        types.InlineKeyboardButton(text='❌', callback_data=f'book deny {updated_range}'),
    )
    for admin in ADMINS:
        try:
            await bot.send_message(
                admin,
                text=text,
                reply_markup=kb
            )
        except Exception as ex:
            pass
