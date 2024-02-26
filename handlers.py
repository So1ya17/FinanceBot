from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command

from aiogram import flags
from aiogram.fsm.context import FSMContext
from states import Gen
from aiogram.types.callback_query import CallbackQuery

import kb
import text

import sqlite3

router = Router()

def init_db():
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute(
        '''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, balance REAL, total_income REAL, total_expense REAL, piggy_bank REAL)''')
    conn.commit()
    conn.close()

init_db()

@router.message(Command('start'))
async def start_message(msg: Message, state: FSMContext):
    try:
        with sqlite3.connect('bot_data.db') as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM users WHERE id = ?", (msg.from_user.id,))
            user_exists = c.fetchone()
    except sqlite3.Error as e:
        print(f"Ошибка при проверке существования пользователя: {e} 🚫")
        user_exists = None

    if user_exists:
        await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)
    else:
        try:
            with sqlite3.connect('bot_data.db') as conn:
                c = conn.cursor()
                c.execute(
                    "INSERT INTO users (id, username, balance, total_income, total_expense, piggy_bank) VALUES (?, ?, ?, ?, ?, ?)",
                    (msg.from_user.id, msg.from_user.username, 0, 0, 0, 0))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при вставке пользовательских данных: {e} 🚫")

        finally:
            await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)

@router.message(F.text=='Меню')
@router.message(F.text=='Выйти в меню')
async def main_menu(msg: Message):
    await msg.answer(text.menu, reply_markup=kb.menu)

@router.callback_query(F.data == 'set_balance')
async def input_set_balance(clbk: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.balance_set)
    await clbk.message.edit_text(text.gen_balance)
    await clbk.message.answer(text.gen_sup, reply_markup=kb.exit_kb)

@router.message(Gen.balance_set)
@flags.chat_action('typing')
async def save_balance(msg: Message, state: FSMContext):
    balance = float(msg.text)
    await state.update_data(balance=balance)
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute(
        "UPDATE users SET balance = ?, total_income = total_income, total_expense = total_expense WHERE id = ?",
        (balance, msg.from_user.id))

    conn.commit()  # commit the changes
    conn.close()
    await msg.answer('Баланс сохранен ✅\n'
                     '\n'
                     f"Ваш баланс <b>{balance}</b> ✅")

@router.callback_query(F.data == 'add_income')
async def input_add_income(clbk: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.income_add)
    await clbk.message.edit_text(text.gen_income)
    await clbk.message.answer(text.gen_sup2, reply_markup=kb.exit_kb)

@router.message(Gen.income_add)
@flags.chat_action('typing')
async def save_income(msg: Message, state: FSMContext):
    income = float(msg.text)
    data = await state.get_data()
    if 'balance' not in data:
        data['balance'] = 0
    data['balance'] += income
    if 'total_income' not in data:
        data['total_income'] = 0
    data['total_income'] += income
    await state.set_data(data)
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + ?, total_income = total_income + ? WHERE id = ?",
              (income, income, msg.from_user.id))
    conn.commit()
    conn.close()
    await msg.answer('Доход внесен ✅\n'
                     '\n'
                     f"Ваш баланс <b>{data['balance']}</b> ✅")

@router.callback_query(F.data == 'add_expense')
async def input_add_expense(clbk: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.expense_add)
    await clbk.message.edit_text(text.gen_expense)
    await clbk.message.answer(text.gen_sup2, reply_markup=kb.exit_kb)

@router.message(Gen.expense_add)
@flags.chat_action('typing')
async def save_expense(msg: Message, state: FSMContext):
    expense = float(msg.text)
    data = await state.get_data()
    if 'balance' not in data:
        data['balance'] = 0
    data['balance'] -= expense
    if 'total_expense' not in data:
        data['total_expense'] = 0
    data['total_expense'] += expense
    await state.set_data(data)
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance - ?, total_expense = total_expense + ? WHERE id = ?",
              (expense, expense, msg.from_user.id))
    conn.commit()
    conn.close()
    await msg.answer('Расход внесен ✅\n'
                     '\n'
                     f"Ваш баланс <b>{data['balance']}</b> ✅")

@router.callback_query(F.data == 'view_base')
async def view_base_all(clbk: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.base_view)
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute("SELECT balance, total_income, total_expense, piggy_bank FROM users WHERE id = ?", (clbk.from_user.id,))
    user_data = c.fetchone()
    conn.close()

    if user_data is None:
        await clbk.message.edit_text('Не удалось найти ваши данные в базе 🚫')
    else:
        balance, total_income, total_expense, piggy_bank = user_data
        await clbk.message.edit_text(f'🔹Ваш текущий баланс: <b>{balance:.2f}</b>\n'
                                     f'🔹Ваш общий доход: <b>{total_income:.2f}</b>\n'
                                     f'🔹Ваши общие расходы: <b>{total_expense:.2f}</b>\n'
                                     f'🔹Ваша копилка: <b>{piggy_bank:.2f}</b>')
        await clbk.message.answer(text.gen_sup3, reply_markup=kb.exit_kb)


@router.message(Gen.base_view)
@flags.chat_action('typing')
async def watch_view_all(msg: Message, state: FSMContext):
    await msg.answer(text.gen_iexit)

@router.callback_query(F.data == 'reset')
async def view_base_all(clbk: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.reset_info)
    await clbk.message.edit_text(text.gen_reset)
    await clbk.message.answer(text.gen_reset2, reply_markup=kb.exit_kb)

@router.message(Gen.reset_info)
async def reset_all(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    user_data = await state.get_data()

    if msg.text.lower() == 'да':
        conn = sqlite3.connect('bot_data.db')
        c = conn.cursor()

        try:
            c.execute("UPDATE users SET balance = 0, total_income = 0, total_expense = 0, piggy_bank = 0 WHERE id = ?",
                      (user_id,))
            conn.commit()
            await msg.answer(text.reset_success, reply_markup=kb.exit_kb)
        except sqlite3.Error as e:
            print(f"Error while resetting user data: {e} 🚫")
            await msg.answer(text.reset_error)
        finally:
            conn.close()
    elif msg.text.lower() == 'нет':
        await msg.answer(text.return_menu, reply_markup=kb.menu)
    else:
        await msg.answer(text.invalid_input)

@router.callback_query(F.data == 'piggy_bank')
async def bank(clbk: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.bank_piggy)
    await clbk.message.edit_text(text.gen_bank)
    await clbk.message.answer(text.gen_add_remove, reply_markup=kb.iadd_remove)

@router.callback_query(F.data == 'add_bank')
async def add_bank(clbk: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.bank_add)
    await clbk.message.answer('Сколько хотите внести в копилку? 🐽')

@router.message(Gen.bank_add)
async def save_add_bank(msg: Message, state: FSMContext):
    amount = float(msg.text)
    data = await state.get_data()
    if 'balance' not in data:
        data['balance'] = 0
    if 'piggy_bank' not in data:
        data['piggy_bank'] = 0
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute("SELECT balance, piggy_bank FROM users WHERE id = ?", (msg.from_user.id,))
    current_balance, current_piggy_bank = c.fetchone()
    if current_balance >= amount:
        data['balance'] = current_balance - amount
        data['piggy_bank'] = current_piggy_bank + amount
        c.execute("UPDATE users SET balance = ?, piggy_bank = ? WHERE id = ?",
                  (data['balance'], data['piggy_bank'], msg.from_user.id))
        conn.commit()
        conn.close()
        await msg.answer(f'Вы внесли <b>{amount}</b> ✅\n'
                         f'\n'
                         f"В копилке <b>{data['piggy_bank']}</b> ✅\n"
                         f"На вашем балансе <b>{data['balance']}</b> ✅", reply_markup=kb.exit_kb)
    else:
        await msg.answer('На вашем балансе недостаточно средств для такой операции 🚫')

@router.callback_query(F.data == 'remove_bank')
async def remove_bank(clbk: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.bank_remove)
    await clbk.message.answer('Сколько хотите забрать из копилки? 🐽')

@router.message(Gen.bank_remove)
async def save_remove_bank(msg: Message, state: FSMContext):
    amount = float(msg.text)
    data = await state.get_data()
    if 'piggy_bank' not in data:
        data['piggy_bank'] = 0
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute("SELECT balance, piggy_bank FROM users WHERE id = ?", (msg.from_user.id,))
    current_balance, current_piggy_bank = c.fetchone()
    if current_piggy_bank is not None and current_piggy_bank >= amount:
        data['piggy_bank'] = current_piggy_bank - amount
        data['balance'] = current_balance + amount
        c.execute("UPDATE users SET balance = ?, piggy_bank = ? WHERE id = ?",
                  (data['balance'], data['piggy_bank'], msg.from_user.id))
        conn.commit()
        conn.close()
        await msg.answer(f'Вы сняли <b>{amount}</b> ✅\n'
                         f'\n'
                         f"В копилке <b>{data['piggy_bank']}</b> ✅\n"
                         f"На вашем балансе <b>{data['balance']}</b> ✅", reply_markup=kb.exit_kb)
    else:
        await msg.answer(f'На вашей копилке недостаточно средств для снятия <b>{amount}</b> 🚫\n'
                         f'На копилке только <b>{current_piggy_bank}</b> 🚫')