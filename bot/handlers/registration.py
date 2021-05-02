import asyncio
from datetime import datetime

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

С помощью MeetPeer ты сможешь найти новые знакомства с людьми, которые учатся или учились в твоем университете.

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


async def stage_grad_year(message: types.Message, state: FSMContext):
    try:
        int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, укажи год выпуска")
    else:
        await AirtableAPI.update_user(
            message.from_user.id, state=UserState.grad_year, grad_year=int(message.text)
        )
        keyboard = types.ReplyKeyboardMarkup()
        buttons = [
            types.KeyboardButton(text="1 раз (Бесплатно)"),
            types.KeyboardButton(text="3 раза (100 рублей в месяц)"),
        ]
        keyboard.add(*buttons)
        await message.answer(
            "Последний вопрос 🙂\n\nСколько раз в неделю тебе искать пару для общения?",
            reply_markup=keyboard,
        )
        await RegisterSteps.next()


async def stage_payment(message: types.Message, state: FSMContext):
    if message.text == "1 раз (Бесплатно)":
        await AirtableAPI.update_user(
            message.from_user.id,
            state=UserState.payment,
            frequency=1,
            frequency_updated=str(datetime.utcnow()),
        )
        keyboard = types.ReplyKeyboardMarkup()
        buttons = [
            types.KeyboardButton(text="Все понятно!"),
        ]
        keyboard.add(*buttons)
        await message.answer(
            "Отлично! Ты всегда сможешь увеличить количество встреч через команду /payment",
            reply_markup=keyboard,
        )
    elif message.text == "3 раза (100 рублей в месяц)":
        await AirtableAPI.update_user(
            message.from_user.id,
            state=UserState.payment,
            frequency=1,
            frequency_updated=str(datetime.utcnow()),
            payment_pending=True,
        )
        await message.answer(
            "Отличное решение! Так ты сможешь быстро построить сеть полезных знакомств!\n\nПожалуйста, познакомься с Пользовательским соглашением. Оплата предполагает, что ты ознакомлен с этими правилами.",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        await message.answer("https://disk.yandex.ru/i/8tLxmWvFp28-Bg")
        await asyncio.sleep(10)
        keyboard = types.ReplyKeyboardMarkup()
        buttons = [
            types.KeyboardButton(text="Оплата произведена ✅"),
        ]
        keyboard.add(*buttons)
        await message.answer(
            "Оплату можно произвести по ссылке — https://yoomoney.ru/to/410019123578551\n\nВ комментарии к платежу обязательно укажи свой username.",
            reply_markup=keyboard,
        )
    await RegisterSteps.next()


async def stage_active(message: types.Message, state: FSMContext):
    if message.text == "Оплата произведена ✅":
        await message.answer(
            "Мы обработаем платеж в течение суток, с новой недели ты будешь получать три новых контакта для знакомства!",
            reply_markup=types.ReplyKeyboardRemove(),
        )
    elif message.text == "Все понятно!":
        await message.answer("Супер!", reply_markup=types.ReplyKeyboardRemove())
    await AirtableAPI.update_user(message.from_user.id, state=UserState.active)
    await message.answer("Записал тебя. В понедельник пришлю контакты для встреч!")
    await message.answer(
        "Ты сможешь изменить свои настройки через команду /settings. Связаться с нами можно через команду /contact.\n\nНадеемся, что ты найдешь отличные знакомства через MeetPeer!"
    )
    await state.finish()
