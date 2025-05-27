import logging
import json
import httpx

api_url = "https://api.telegram.org"

logger = logging.getLogger(__name__)


async def make_api_post(request_url: str, data, async_client: httpx.AsyncClient):
    try:
        response = await async_client.post(request_url, data=data)
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(
            f"error response {e.response.status_code} for request {e.request.url}"
        )
    except httpx.RequestError as e:
        logger.error(f"error making request {e.request.url} - {e}")
    except json.JSONDecodeError as e:
        logger.error(f"error decoding json in response {e.doc} at position {e.pos}")

    return None


async def make_api_get(request_url: str, async_client: httpx.AsyncClient):
    try:
        response = await async_client.get(request_url)
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(
            f"error response {e.response.status_code} for request {e.request.url}"
        )
    except httpx.RequestError as e:
        logger.error(f"error making request {e.request.url}")
    except json.JSONDecodeError as e:
        logger.error(f"error decoding json in response {e.doc} at position {e.pos}")

    return None


async def send_message(
    token: str, chat_id: str, text: str, async_client: httpx.AsyncClient
):
    token = "bot" + token

    request_url = "/".join([api_url, token, "sendMessage"])

    return await make_api_post(
        request_url,
        {"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
        async_client,
    )


async def edit_message_text(
    token: str,
    chat_id: str,
    message_id: str,
    text: str,
    async_client: httpx.AsyncClient,
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
    )


async def get_me(token: str, async_client: httpx.AsyncClient):
    token = "bot" + token
    request_url = "/".join([api_url, token, "getMe"])

    return await make_api_get(request_url, async_client)
