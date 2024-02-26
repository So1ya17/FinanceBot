from aiogram.fsm.state import StatesGroup, State

class Gen(StatesGroup):
    income_add = State()
    expense_add = State()
    balance_set = State()
    base_view = State()
    bank_piggy = State()
    reset_info = State()
    bank_add = State()
    bank_remove = State()