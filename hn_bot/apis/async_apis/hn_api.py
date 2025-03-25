# This file implements a simple interface for the public HN API using httpx' async client
# Currently only synchronous methods are provided, this may change in the future.
import httpx
from hn_bot.bot_config import BotConfig

api_url = "https://hacker-news.firebaseio.com"
api_version = "v0"


async def get_json(request_url: str):
    try:
        response = await BotConfig.get().async_http_client.get(request_url)
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f"HTTP Error: {e.response.status_code}")
    except httpx.RequestError as e:
        print(f"RequestError: {e.request.url!r}")

    # error handling here
    return None


async def get(request_params: list[str]):
    request_url = "/".join(request_params)
    return await get_json(request_url)


async def get_root(file: str):
    return await get([api_url, api_version, file])


async def get_item(id: str):
    endpoint = "item"
    file = f"{id}.json"

    return await get([api_url, api_version, endpoint, file])


async def get_user(name: str):
    endpoint = "user"
    file = f"{name}.json"

    return await get([api_url, api_version, endpoint, file])


async def get_maxitem():
    file = "maxitem.json"
    return await get_root(file)


async def get_topstories():
    file = "topstories.json"
    return await get_root(file)


async def get_newstories():
    file = "newstories.json"
    return await get_root(file)


async def get_beststories():
    file = "beststories.json"
    return await get_root(file)


async def get_askstories():
    file = "askstories.json"
    return await get_root(file)


async def get_showstories():
    file = "showstories.json"
    return await get_root(file)


async def get_jobstories():
    file = "jobstories.json"
    return await get_root(file)


async def get_updates():
    file = "updates.json"
    return await get_root(file)
