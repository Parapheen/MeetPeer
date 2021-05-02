import asyncio
from datetime import datetime

from aiogram import types

from ..airtable import AirtableAPI
from ..states import UserState


async def contact(message: types.Message):
    await message.answer(
        "Пожалуйста, свяжись с нами через форму\n\nhttps://forms.gle/kUanUGxUmhNokgsh8"
    )


async def change_status(message: types.Message):
    user = await AirtableAPI.get_user(message.from_user.id)
    state = user["records"][0]["fields"].get("state")
    if state == UserState.active:
        await AirtableAPI.update_user(message.from_user.id, state=UserState.inactive)
        await message.answer(
            "Ок. Поставил паузу.\n\nВозобновить встречи можно через эту же команду."
        )
    elif state == UserState.inactive:
        await AirtableAPI.update_user(message.from_user.id, state=UserState.active)
        await message.answer("Ок. Жди сообщения на следующей неделе!")


async def change_payment(message: types.Message):
    user = await AirtableAPI.get_user(message.from_user.id)
    frequency = user["records"][0]["fields"].get("frequency")
    if str(frequency) == "1":
        await AirtableAPI.update_user(
            message.from_user.id,
            frequency=1,
            frequency_updated=str(datetime.utcnow()),
            payment_pending=True,
        )
        await message.answer(
            "Отличное решение! Так ты сможешь быстро построить сеть полезных знакомств!\n\nПожалуйста, познакомься с Пользовательским соглашением. Оплата предполагает, что ты ознакомлен с этими правилами.",
        )
        await message.answer("https://disk.yandex.ru/i/8tLxmWvFp28-Bg")
        await asyncio.sleep(10)
        await message.answer(
            "Оплату можно произвести по ссылке — https://yoomoney.ru/to/410019123578551\n\nВ комментарии к платежу обязательно укажи свой username.",
        )
        await asyncio.sleep(5)
        await message.answer(
            "Мы обработаем платеж в течение суток, с новой недели ты будешь получать три новых контакта для знакомства!",
        )
    elif str(frequency) == "3":
        await AirtableAPI.update_user(
            message.from_user.id,
            frequency=1,
            frequency_updated=str(datetime.utcnow()),
        )
        await message.answer(
            "Ок. Перевожу тебя на бесплатный тарифный план. Если захочешь вернуться к трем встречам в неделю, используй команду /payment"
        )
