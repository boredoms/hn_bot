import httpx
import json
import logging

api_url = "https://api.telegram.org"

logger = logging.getLogger(__name__)


def make_api_post(request_url: str, data):
    try:
        response = httpx.post(request_url, data=data)
        return response.json()
    except json.JSONDecodeError as e:
        logger.error(f"error decoding json in response {e.doc} at position {e.pos}")
    except httpx.HTTPError as exc:
        logger.error(f"HTTP Error - {type(exc)}: {exc}")

    return None


def make_api_get(request_url: str):
    try:
        response = httpx.get(request_url)
        return response.json()
    except json.JSONDecodeError as e:
        logger.error(f"error decoding json in response {e.doc} at position {e.pos}")
    except httpx.HTTPError as exc:
        logger.error(f"HTTP Error - {type(exc)}: {exc}")

    return None


def send_message(token: str, chat_id: str, text: str):
    token = "bot" + token

    request_url = "/".join([api_url, token, "sendMessage"])

    return make_api_post(
        request_url, {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    )


def edit_message_text(token: str, chat_id: str, message_id: str, text: str):
    token = "bot" + token

    request_url = "/".join([api_url, token, "editMessageText"])

    return make_api_post(
        request_url,
        {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "HTML",
        },
    )


def get_me(token: str):
    token = "bot" + token
    request_url = "/".join([api_url, token, "getMe"])

    return make_api_get(request_url)
