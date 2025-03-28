from hn_bot.bot_config import BotConfig
import logging
import json
import httpx

api_url = "https://api.telegram.org"

_async_client = BotConfig.get().async_http_client
logger = logging.getLogger(__name__)


async def make_api_post(request_url: str, data):
    try:
        response = await _async_client.post(request_url, data=data)
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


async def make_api_get(request_url: str):
    try:
        response = await _async_client.get(request_url)
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


async def send_message(token: str, chat_id: str, text: str):
    token = "bot" + token

    request_url = "/".join([api_url, token, "sendMessage"])

    return await make_api_post(
        request_url, {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    )


async def edit_message_text(token: str, chat_id: str, message_id: str, text: str):
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
    )


async def get_me(token: str):
    token = "bot" + token
    request_url = "/".join([api_url, token, "getMe"])

    return await make_api_get(request_url)
