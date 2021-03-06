import argparse

from aiogram import Bot, Dispatcher, executor, filters
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand

from .settings import BotConfig, AirtableConfig
from .handlers import registration, extra, admin, matcher
from .logger import get_logger
from .states import RegisterSteps
from .middlewares import ThrottlingMiddleware

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
    dp.register_message_handler(
        admin.send_message,
        filters.IDFilter(user_id=BotConfig.ADMINS),
        commands=["send"],
    )
    dp.register_message_handler(
        admin.ask_for_feedback,
        filters.IDFilter(user_id=BotConfig.ADMINS),
        commands=["feedback"],
    )
    dp.register_message_handler(
        admin.send_push,
        filters.IDFilter(user_id=BotConfig.ADMINS),
        commands=["push"],
    )
    dp.register_message_handler(
        matcher.randomize,
        filters.IDFilter(user_id=BotConfig.ADMINS),
        commands=["roll"],
    )

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


async def on_startup(dp: Dispatcher):
    await set_commands(dp.bot)
    dp.middleware.setup(ThrottlingMiddleware())
    register_handlers(dp)


def get_bot(dev: bool = False):
    logger.info("Starting bot")
    if dev:
        bot = Bot(token=BotConfig.TOKEN_DEV)
    else:
        bot = Bot(token=BotConfig.TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    return dp


parser = argparse.ArgumentParser()
parser.add_argument(
    "--mode", dest="mode", required=True, help="Bot mode", choices=["prod", "dev"]
)
args = parser.parse_args()
dev = False
if args.mode == "dev":
    AirtableConfig.set_dev()
    dev = True
dp = get_bot(dev)
executor.start_polling(dp, on_startup=on_startup)
