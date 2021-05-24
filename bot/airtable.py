import aiohttp
from dataclasses import asdict

from bot.settings import AirtableConfig
from bot.models import User
from bot.logger import get_logger
from bot.exceptions import AirtableRequestError

logger = get_logger(__name__)


class AirtableAPI:
    async def get_user(tg_id: str):
        column = "tg_id"
        params = {"filterByFormula": f"{column}='{tg_id}'"}

        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(
                    AirtableConfig.USERS, params=params, headers=AirtableConfig.HEADERS
                ) as r:
                    resp = await r.json()
        except (aiohttp.ClientResponseError, aiohttp.ClientConnectorError):
            logger.exception("Problem when sending request")
            raise
        else:
            if "error" in resp:
                raise AirtableRequestError(resp["error"]["message"])
            else:
                return resp

    async def get_current_pairs():
        column = "feedback_message"
        params = {"filterByFormula": f"NOT({column})"}

        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(
                    AirtableConfig.PAIRS, params=params, headers=AirtableConfig.HEADERS
                ) as r:
                    resp = await r.json()
        except (aiohttp.ClientResponseError, aiohttp.ClientConnectorError):
            logger.exception("Problem when sending request")
            raise
        else:
            if "error" in resp:
                raise AirtableRequestError(resp["error"]["message"])
            else:
                return resp

    async def get_users_to_push():
        column = "state"
        params = {"filterByFormula": f"{column}<6"}

        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(
                    AirtableConfig.USERS, params=params, headers=AirtableConfig.HEADERS
                ) as r:
                    resp = await r.json()
        except (aiohttp.ClientResponseError, aiohttp.ClientConnectorError):
            logger.exception("Problem when sending request")
            raise
        else:
            if "error" in resp:
                raise AirtableRequestError(resp["error"]["message"])
            else:
                return resp

    async def get_active_users():
        column = "state"
        params = {"filterByFormula": f"AND({column}>=6, {column}!=8)"}
        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(
                    AirtableConfig.USERS, params=params, headers=AirtableConfig.HEADERS
                ) as r:
                    resp = await r.json()
        except (aiohttp.ClientResponseError, aiohttp.ClientConnectorError):
            logger.exception("Problem when sending request")
            raise
        else:
            if "error" in resp:
                raise AirtableRequestError(resp["error"]["message"])
            else:
                return resp

    async def create_user(**kwargs):
        user = User(**kwargs)
        user_dict = asdict(user)
        data = {"fields": user_dict}
        get_user = await AirtableAPI.get_user(user.tg_id)
        if (
            get_user["records"]
            and get_user["records"][0]["fields"]["tg_id"] == user.tg_id
        ):
            logger.info("User already exists")
            return

        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.post(
                    AirtableConfig.USERS, json=data, headers=AirtableConfig.HEADERS
                ) as r:
                    resp = await r.json()
        except (aiohttp.ClientResponseError, aiohttp.ClientConnectorError):
            logger.exception("Problem when sending request")
            raise
        else:
            if "error" in resp:
                logger.error("Error response from adding participant to airtable")
                raise AirtableRequestError(resp["error"]["message"])
            else:
                logger.info("Succesfully added user in Airtable")
                return resp

    async def update_user(tg_id: str, **kwargs):
        airtable_row = await AirtableAPI.get_user(tg_id)
        if not airtable_row["records"]:
            return
        data = {"records": [{"id": airtable_row["records"][0]["id"], "fields": kwargs}]}
        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.patch(
                    AirtableConfig.USERS, json=data, headers=AirtableConfig.HEADERS
                ) as r:
                    resp = await r.json()
        except (aiohttp.ClientResponseError, aiohttp.ClientConnectorError) as e:
            raise
        else:
            if "error" in resp:
                raise AirtableRequestError(resp["error"]["message"])
            else:
                logger.info(f"SUCCESSFULLY updated Airtable user {tg_id} — {kwargs}")

    async def get_pair(user_a: str, user_b: str):
        column_a = "user_a"
        column_b = "user_b"
        params = {
            "filterByFormula": f"AND({column_a}='{user_a}', {column_b}='{user_b}')"
        }

        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(
                    AirtableConfig.PAIRS, params=params, headers=AirtableConfig.HEADERS
                ) as r:
                    resp = await r.json()
        except (aiohttp.ClientResponseError, aiohttp.ClientConnectorError):
            logger.exception("Problem when sending request")
            raise
        else:
            if "error" in resp:
                raise AirtableRequestError(resp["error"]["message"])
            else:
                return resp

    async def update_pair(user_a: str, user_b: str, **kwargs):
        airtable_row = await AirtableAPI.get_pair(user_a, user_b)
        if not airtable_row["records"]:
            return
        data = {"records": [{"id": airtable_row["records"][0]["id"], "fields": kwargs}]}
        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.patch(
                    AirtableConfig.PAIRS, json=data, headers=AirtableConfig.HEADERS
                ) as r:
                    resp = await r.json()
        except (aiohttp.ClientResponseError, aiohttp.ClientConnectorError) as e:
            raise
        else:
            if "error" in resp:
                raise AirtableRequestError(resp["error"]["message"])
            else:
                logger.info(
                    f"SUCCESSFULLY updated Airtable pair {user_a}, {user_b} — {kwargs}"
                )
