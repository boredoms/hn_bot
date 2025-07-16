import asyncio
import json
import logging
import random

import httpx

from hn_bot.rate_limiter import RateLimiter

api_url = "https://api.telegram.org"

logger = logging.getLogger(__name__)


async def make_api_post(
    request_url: str, data, async_client: httpx.AsyncClient, rate_limiter: RateLimiter
):
    num_tries = 0
    sleep_time = 5.0
    while num_tries < 3:
        await rate_limiter.wait()

        try:
            response = await async_client.post(request_url, data=data)
            return response.json()
        except json.JSONDecodeError as e:
            logger.error(f"error decoding json in response {e.doc} at position {e.pos}")
        except httpx.HTTPError as exc:
            logger.error(f"HTTP Error - {type(exc)}: {exc}")

        sleep_time += random.normalvariate(sigma=num_tries + 1)

        await asyncio.sleep(sleep_time)

        num_tries += 1
        sleep_time *= 2

    logger.error(
        f"too many errors for request_url {request_url} with data: {data} - giving up"
    )
    return None


async def make_api_get(request_url: str, async_client: httpx.AsyncClient):
    num_tries = 0
    sleep_time = 5.0
    while num_tries < 3:
        try:
            response = await async_client.get(request_url)
            return response.json()
        except json.JSONDecodeError as e:
            logger.error(f"error decoding json in response {e.doc} at position {e.pos}")
        except httpx.HTTPError as exc:
            logger.error(f"HTTP Error - {type(exc)}: {exc}")

        sleep_time += random.normalvariate(sigma=num_tries + 1)

        await asyncio.sleep(sleep_time)

        num_tries += 1
        sleep_time *= 2

    logger.error(f"too many errors for request_url {request_url} - giving up")
    return None


async def send_message(
    token: str,
    chat_id: str,
    text: str,
    async_client: httpx.AsyncClient,
    rate_limiter: RateLimiter,
):
    token = "bot" + token

    request_url = "/".join([api_url, token, "sendMessage"])

    return await make_api_post(
        request_url,
        {"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
        async_client,
        rate_limiter,
    )


async def edit_message_text(
    token: str,
    chat_id: str,
    message_id: str,
    text: str,
    async_client: httpx.AsyncClient,
    rate_limiter: RateLimiter,
):
    token = "bot" + token

    request_url = "/".join([api_url, token, "editMessageText"])

    return await make_api_post(
        request_url,
        {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "HTML",
        },
        async_client,
        rate_limiter,
    )


async def get_me(token: str, async_client: httpx.AsyncClient):
    token = "bot" + token
    request_url = "/".join([api_url, token, "getMe"])

    return await make_api_get(request_url, async_client)
