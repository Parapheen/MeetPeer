import os
from dotenv import load_dotenv

from dataclasses import dataclass

load_dotenv(override=True)


@dataclass
class BotConfig:
    TOKEN = os.getenv("BOT_TOKEN")
    TOKEN_DEV = os.getenv("BOT_DEV")


@dataclass
class AirtableConfig:
    TOKEN = os.getenv("AIRTABLE_TOKEN")
    APP_ID = os.getenv("AIRTABLE_APP_ID")

    BASE_URL = "https://api.airtable.com/v0/{}/".format(APP_ID)
    HEADERS = {"Authorization": "Bearer {}".format(TOKEN)}

    USERS = f"{BASE_URL}Users"
