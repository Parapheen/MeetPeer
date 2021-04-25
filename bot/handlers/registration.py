from aiogram import Bot, types
from aiogram.dispatcher import FSMContext

from bot.states import RegisterSteps, UserState
from bot.airtable import AirtableAPI

async def cmd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup()
    start_button = types.KeyboardButton(text="Поехали!")
    keyboard.add(start_button)
    await message.answer(
        f"""Привет, {message.from_user.username}!

С помощью MeetPeer ты сможешь найти новые знакомства с людьми из твоего университета.

Все очень просто:
1) Раз в неделю бот рандомно распределяет всех участников из одного вуза
2) Вы подтверждаете встречу и договариваетесь о звонке или личной встрече
3) Знакомитесь и обмениваетесь опытом!

Начнем?
        """, reply_markup=keyboard
    )
    await AirtableAPI.create_user(username=message.from_user.username)
    await RegisterSteps.go.set()


async def cmd_text_go(message: types.Message, state: FSMContext):
    await AirtableAPI.update_user(message.from_user.username, state=UserState.go)
    await message.answer('Супер! Расскажи немного о себе. Это поможет избавиться от глупого молчания при встрече.\n\nКак тебя зовут?', reply_markup=types.ReplyKeyboardRemove())
    await RegisterSteps.next()