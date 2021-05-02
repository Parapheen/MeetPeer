from enum import Enum
from aiogram.dispatcher.filters.state import State, StatesGroup


class UserState(int, Enum):
    start = 0
    go = 1
    name = 2
    is_graduate = 3
    university = 4
    grad_year = 5
    payment = 6
    active = 7
    inactive = 8


class RegisterSteps(StatesGroup):
    go = State()
    name = State()
    is_graduate = State()
    university = State()
    grad_year = State()
    payment = State()
    active = State()
