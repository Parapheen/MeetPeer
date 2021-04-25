import aiohttp
from dataclasses import asdict

from bot.settings import AirtableConfig
from bot.models import User
from bot.logger import get_logger
from bot.exceptions import AirtableRequestError

logger = get_logger(__name__)

class AirtableAPI:


	async def get_user(username: str):
		column = 'username'
		params = {"filterByFormula": f"{column}='{username}'"}

		try:
			async with aiohttp.ClientSession() as cs:
				async with cs.get(AirtableConfig.USERS, params=params, headers=AirtableConfig.HEADERS) as r:
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
		data = {
			"fields": user_dict
		}
		get_user = await AirtableAPI.get_user(user.username)
		if get_user['records'] and get_user['records'][0]['fields']['username'] == user.username:
			logger.info("User already exists")
			return

		try:
			async with aiohttp.ClientSession() as cs:
				async with cs.post(AirtableConfig.USERS, json=data, headers=AirtableConfig.HEADERS) as r:
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

	async def update_user(username: str, **kwargs):
		user = User(username=username, **kwargs)
		user_dict = asdict(user)
		airtable_row = await AirtableAPI.get_user(user.username)
		if not airtable_row['records']:
			return
		data = {"records": [{"id": airtable_row['records'][0]['id'], "fields": user_dict}]}
		try:
			async with aiohttp.ClientSession() as cs:
				async with cs.patch(AirtableConfig.USERS, json=data, headers=AirtableConfig.HEADERS) as r:
					resp = await r.json()
		except (aiohttp.ClientResponseError, aiohttp.ClientConnectorError) as e:
			raise
		else:
			if "error" in resp:
				raise AirtableRequestError(resp["error"]["message"])
			else:
				logger.info("SUCCESSFULLY updated Airtable user")