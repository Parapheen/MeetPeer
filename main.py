import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand

from bot.settings import BotConfig
from bot.handlers import registration
from bot.logger import get_logger
from bot.states import RegisterSteps

logger = get_logger(__name__)

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/contact", description="Contact us"),
    ]
    await bot.set_my_commands(commands)


async def main():
    logger.info("Starting bot")
    bot = Bot(token=BotConfig.TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    await set_commands(bot)

    dp.register_message_handler(registration.cmd_start, commands=["start"])
    dp.register_message_handler(registration.cmd_text_go, state=RegisterSteps.go)

    try:
        await dp.start_polling()
    finally:
        await bot.close()


if __name__ == '__main__':
    asyncio.run(main())