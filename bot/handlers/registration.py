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
        """,
        reply_markup=keyboard,
    )
    await AirtableAPI.create_user(
        tg_id=message.from_user.id, username=message.from_user.username
    )
    await RegisterSteps.go.set()


async def cmd_text_go(message: types.Message, state: FSMContext):
    await AirtableAPI.update_user(message.from_user.id, state=UserState.go)
    await message.answer(
        "Супер! Расскажи немного о себе. Это поможет избавиться от глупого молчания при встрече.\n\nКак тебя зовут?",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await RegisterSteps.next()


async def stage_name(message: types.Message, state: FSMContext):
    await AirtableAPI.update_user(
        message.from_user.id, state=UserState.name, name=message.text
    )
    await message.reply(f"Приятно познакомиться, {message.text}!")
    keyboard = types.ReplyKeyboardMarkup()
    buttons = [
        types.KeyboardButton(text="Студент"),
        types.KeyboardButton(text="Выпускник"),
    ]
    keyboard.add(*buttons)
    await message.answer("Ты студент или выпускник?", reply_markup=keyboard)
    await RegisterSteps.next()


async def stage_graduate(message: types.Message, state: FSMContext):
    if message.text == "Студент":
        await AirtableAPI.update_user(
            message.from_user.id, state=UserState.is_graduate, is_graduate=False
        )
        await message.answer(
            "Круто 😎\n\nГде ты учишься? Мы постараемся подобрать студентов и выпускников из твоего вуза.",
            reply_markup=types.ReplyKeyboardRemove(),
        )
    elif message.text == "Выпускник":
        await AirtableAPI.update_user(
            message.from_user.id, state=UserState.is_graduate, is_graduate=True
        )
        await message.answer(
            "Круто 😎\n\nВыпускником какого вуза ты являешься? Мы постараемся подобрать студентов и выпускников из твоего вуза.",
            reply_markup=types.ReplyKeyboardRemove(),
        )
    else:
        await message.answer(
            "Пожалуйста, укажи являешься ли ты студентом или выпускником."
        )
        return
    await RegisterSteps.next()


async def stage_university(message: types.Message, state: FSMContext):
    await AirtableAPI.update_user(
        message.from_user.id, state=UserState.university, university=message.text
    )
    user = await AirtableAPI.get_user(message.from_user.id)
    is_graduate = user["records"][0]["fields"].get("is_graduate")
    if is_graduate:
        await message.answer("В каком году ты выпустился(-ась)?")
    else:
        await message.answer("В каком году ты выпускаешься?")
    await RegisterSteps.next()
