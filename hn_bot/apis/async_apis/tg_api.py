from hn_bot.bot_config import BotConfig

api_url = "https://api.telegram.org"

_async_client = BotConfig.get().async_http_client


async def send_message(token: str, chat_id: str, text: str):
    token = "bot" + token

    request_url = "/".join([api_url, token, "sendMessage"])

    response = await _async_client.post(
        request_url, data={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    )

    return response.json()


async def edit_message_text(token: str, chat_id: str, message_id: str, text: str):
    token = "bot" + token

    request_url = "/".join([api_url, token, "editMessageText"])

    response = await _async_client.post(
        request_url,
        data={
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "HTML",
        },
    )

    return response.json()


async def get_me(token: str):
    token = "bot" + token
    request_url = "/".join([api_url, token, "getMe"])

    response = await _async_client.get(request_url)

    return response.json()
