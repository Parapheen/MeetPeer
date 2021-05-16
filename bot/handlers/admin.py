import asyncio
from aiogram import types, exceptions

from ..logger import get_logger
from ..airtable import AirtableAPI

log = get_logger(__name__)


async def send(bot, user_id: str, text: str, message: types.Message):
    try:
        await bot.send_message(user_id, text)
    except exceptions.BotBlocked:
        log.error(f"Target [ID:{user_id}]: blocked by user")
        await message.reply(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.ChatNotFound:
        log.error(f"Target [ID:{user_id}]: invalid user ID")
        await message.reply(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        log.error(
            f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds."
        )
        await asyncio.sleep(e.timeout)
        return await send_message(user_id, text)  # Recursive call
    except exceptions.UserDeactivated:
        log.error(f"Target [ID:{user_id}]: user is deactivated")
        await message.reply(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        log.exception(f"Target [ID:{user_id}]: failed")
        await message.reply(f"Target [ID:{user_id}]: failed")
    else:
        log.info(f"Target [ID:{user_id}]: success")
        await message.reply(f"Target [ID:{user_id}]: success")
        return True
    return False


async def send_message(message: types.Message):
    bot = message.bot
    user_id = int(message.text.split(" ")[1])
    text = message.text.split(" | ")[-1]
    await send(bot, user_id, text, message)


async def ask_for_feedback(message=types.Message):
    pairs = await AirtableAPI.get_current_pairs()
    user_ids = []
    for pair in pairs["records"]:
        user_ids.append((pair["fields"]["user_a"], pair["fields"]["user_b"]))
    bot = message.bot
    for pair in user_ids:
        for user in pair:
            text = """
Привет!

Надеемся, что вы смогли встретиться/созвониться со своей парой 🙂

Пожалуйста, оставь обратную связь по встрече — https://forms.gle/v5q1gmbKHNq43FNN8.
Там только 3 вопроса :)

В понедельник начинается новый раунд знакомств!
Изменить данные о себе — /settings
Взять паузу — /status
Увеличить количество встреч – /payment
        """
            await send(bot, user, text, message)
        await AirtableAPI.update_pair(pair[0], pair[1], feedback_message=True)


async def send_push(message=types.Message):
    """Send push notifications to finish registration
    for users with status < 6
    """
    users_to_push = await AirtableAPI.get_users_to_push()
    user_ids = [user["fields"]["tg_id"] for user in users_to_push["records"]]
    bot = message.bot
    text = """
Привет!

Следующий круг знакомств начинается в этот понедельник. Заполни свой профиль до конца, чтобы мы смогли найти тебе пару!

Заполнить профиль можно через команду /settings.

До встречи в понедельник!
    """
    for user in user_ids:
        await send(bot, user, text, message)
