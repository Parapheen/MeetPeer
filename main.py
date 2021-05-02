import asyncio
import logging

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand

from bot.settings import BotConfig
from bot.handlers import registration, extra
from bot.logger import get_logger
from bot.states import RegisterSteps
from bot.middlewares import ThrottlingMiddleware

logger = get_logger(__name__)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command="/status", description="Взять паузу от встреч/возобновить встречи"
        ),
        BotCommand(command="/settings", description="Настройки аккаунта"),
        BotCommand(command="/payment", description="Изменить тарифный план"),
        BotCommand(command="/contact", description="Связаться с нами"),
    ]
    await bot.set_my_commands(commands)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(extra.contact, commands=["contact"])
    dp.register_message_handler(extra.change_status, commands=["status"])
    dp.register_message_handler(extra.change_payment, commands=["payment"])

    dp.register_message_handler(registration.cmd_start, commands=["start", "settings"])
    dp.register_message_handler(registration.cmd_text_go, state=RegisterSteps.go)
    dp.register_message_handler(registration.stage_name, state=RegisterSteps.name)
    dp.register_message_handler(
        registration.stage_graduate, state=RegisterSteps.is_graduate
    )
    dp.register_message_handler(
        registration.stage_university, state=RegisterSteps.university
    )
    dp.register_message_handler(
        registration.stage_grad_year, state=RegisterSteps.grad_year
    )
    dp.register_message_handler(registration.stage_payment, state=RegisterSteps.payment)
    dp.register_message_handler(registration.stage_active, state=RegisterSteps.active)


async def get_bot():
    logger.info("Starting bot")
    bot = Bot(token=BotConfig.TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    await set_commands(bot)

    dp.middleware.setup(ThrottlingMiddleware())
    register_handlers(dp)

    return dp


if __name__ == "__main__":
    dp = get_bot()
    executor.start_polling(dp)
