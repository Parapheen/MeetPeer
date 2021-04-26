from enum import Enum
from aiogram.dispatcher.filters.state import State, StatesGroup


class UserState(int, Enum):
    start = 0
    go = 1
    name = 2
    is_graduate = 3
    university = 4
    grad_year = 5
    frequency = 6
    active = 7


class RegisterSteps(StatesGroup):
    go = State()
    name = State()
    is_graduate = State()
    university = State()
    grad_year = State()
    frequency = State()
    active = State()
