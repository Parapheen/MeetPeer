from aiogram import types, exceptions
from ..logger import get_logger

log = get_logger(__name__)


async def send_message(message: types.Message):
    bot = message.bot
    user_id = int(message.text.split(" ")[1])
    text = message.text.split(" | ")[-1]
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
