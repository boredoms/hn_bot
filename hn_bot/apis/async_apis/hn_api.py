# This file implements a simple interface for the public HN API using httpx' async client
# Currently only synchronous methods are provided, this may change in the future.
import httpx
import json
import logging

api_url = "https://hacker-news.firebaseio.com"
api_version = "v0"

logger = logging.getLogger(__name__)


async def get_json(request_url: str, async_client: httpx.AsyncClient):
    try:
        response = await async_client.get(request_url)
        return response.json()
    except json.JSONDecodeError as e:
        logger.error(f"error decoding json in response {e.doc} at position {e.pos}")
    except httpx.HTTPError as exc:
        logger.error(f"HTTP Error - {type(exc)}: {exc}")

    return None


async def get(request_params: list[str], async_client: httpx.AsyncClient):
    request_url = "/".join(request_params)
    return await get_json(request_url, async_client)


async def get_root(file: str, async_client: httpx.AsyncClient):
    return await get([api_url, api_version, file], async_client)


async def get_item(id: str, async_client: httpx.AsyncClient):
    endpoint = "item"
    file = f"{id}.json"

    return await get([api_url, api_version, endpoint, file], async_client)


async def get_user(name: str, async_client: httpx.AsyncClient):
    endpoint = "user"
    file = f"{name}.json"

    return await get([api_url, api_version, endpoint, file], async_client)


async def get_maxitem(async_client: httpx.AsyncClient):
    file = "maxitem.json"
    return await get_root(file, async_client)


async def get_topstories(async_client: httpx.AsyncClient):
    file = "topstories.json"
    return await get_root(file, async_client)


async def get_newstories(async_client: httpx.AsyncClient):
    file = "newstories.json"
    return await get_root(file, async_client)


async def get_beststories(async_client: httpx.AsyncClient):
    file = "beststories.json"
    return await get_root(file, async_client)


async def get_askstories(async_client: httpx.AsyncClient):
    file = "askstories.json"
    return await get_root(file, async_client)


async def get_showstories(async_client: httpx.AsyncClient):
    file = "showstories.json"
    return await get_root(file, async_client)


async def get_jobstories(async_client: httpx.AsyncClient):
    file = "jobstories.json"
    return await get_root(file, async_client)


async def get_updates(async_client: httpx.AsyncClient):
    file = "updates.json"
    return await get_root(file, async_client)
