from enum import Enum
from aiogram.dispatcher.filters.state import State, StatesGroup

class UserState(int, Enum):
	start = 0
	go = 1
	name = 2
	social = 3
	university = 4
	frequency = 5
	active = 6

class RegisterSteps(StatesGroup):
	go = State()
	name = State()
	social = State()
	university = State()
	frequency = State()
	active = State()