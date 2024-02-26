from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

menu = [
    [InlineKeyboardButton(text='Добавить доход💵', callback_data='add_income'),
     InlineKeyboardButton(text='Добавить расход💸', callback_data='add_expense')],
    [InlineKeyboardButton(text='Установить баланс💰', callback_data='set_balance'),
     InlineKeyboardButton(text='Посмотреть данные📊', callback_data='view_base')],
    [InlineKeyboardButton(text='Копилка🐖', callback_data='piggy_bank'),
     InlineKeyboardButton(text='Сбросить🔄', callback_data='reset')]
]

menu = InlineKeyboardMarkup(inline_keyboard=menu)
exit_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Выйти в меню')]], resize_keyboard=True)
iexit_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Выйти в меню', callback_data='menu')]])

iadd_remove = [
    [InlineKeyboardButton(text='Положить', callback_data='add_bank'),
     InlineKeyboardButton(text='Забрать', callback_data='remove_bank')]
]

iadd_remove = InlineKeyboardMarkup(inline_keyboard=iadd_remove)

