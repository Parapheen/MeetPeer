import random

from aiogram import types

from ..airtable import AirtableAPI
from .admin import send

ROLL_MESSAGE = """
Твоя пара на эту неделю — <a href="{tg_id}">{name}</a> {username}, {title} {university}, {grad_year}. 

Советуем прямо сейчас написать и договориться о звонке или встрече 🙂

Не стесняйся написать первым(-ой), твой собеседник уже готов к общению!

"""


async def get_active() -> list:
    users = await AirtableAPI.get_active_users()
    return [u["fields"] for u in users["records"]]


async def assign_groups(users: list):
    group_a = users[: len(users) // 2]
    group_b = users[len(users) // 2 :]

    # if two groups are not equal, add admin to have two matches.
    if len(group_a) > len(group_b):
        parapheen = await AirtableAPI.get_user("94169667")
        group_b.append(parapheen["records"][0]["fields"])
    elif len(group_a) < len(group_b):
        parapheen = await AirtableAPI.get_user("94169667")
        group_a.append(parapheen["records"][0]["fields"])

    return group_a, group_b


async def randomize(message: types.Message):
    users = await get_active()
    bot = message.bot
    random.shuffle(users)
    group_a, group_b = await assign_groups(users)
    pairs = []
    for a, b in zip(group_a, group_b):
        already_paired = await AirtableAPI.get_pair(a["tg_id"], b["tg_id"])
        if already_paired["records"] or a == b:
            await message.reply(
                "В моем рандоме уже есть встретившаяся пара, попробуй еще раз!"
            )
            return
        pairs.append((a, b))
    for pair in pairs:
        user_a = pair[0]
        user_b = pair[1]

        name_a = user_a["name"]
        name_b = user_b["name"]
        tg_id_a = "tg://user?id={}".format(user_a["tg_id"])
        tg_id_b = "tg://user?id={}".format(user_b["tg_id"])
        username_a = "@" + user_a["username"] if "username" in user_a else ""
        username_b = "@" + user_b["username"] if "username" in user_b else ""
        title_a = "студент(-ка)" if "is_graduate" not in user_a else "выпускник(-ца)"
        title_b = "студент(-ка)" if "is_graduate" not in user_b else "выпускник(-ца)"
        university_a = user_a["university"]
        university_b = user_b["university"]
        grad_year_a = user_a["grad_year"]
        grad_year_b = user_b["grad_year"]

        message_a = ROLL_MESSAGE.format(
            name=name_b,
            tg_id=tg_id_b,
            username=username_b,
            title=title_b,
            university=university_b,
            grad_year=grad_year_b,
        )
        message_b = ROLL_MESSAGE.format(
            name=name_a,
            tg_id=tg_id_a,
            username=username_a,
            title=title_a,
            university=university_a,
            grad_year=grad_year_a,
        )

        await send(
            bot,
            user_a["tg_id"],
            message_a,
            message,
            parse_mode=types.ParseMode.HTML,
        )
        await send(
            bot,
            user_b["tg_id"],
            message_b,
            message,
            parse_mode=types.ParseMode.HTML,
        )
        await AirtableAPI.create_pair(int(user_a["tg_id"]), int(user_b["tg_id"]))
