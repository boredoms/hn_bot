import httpx

api_url = "https://api.telegram.org"


def send_message(token: str, chat_id: str, text: str):
    request_url = "/".join([api_url, token, "sendMessage"])

    response = httpx.post(request_url, data={"chat_id": chat_id, "text": text})

    print(response.json())


def get_me(token: str):
    request_url = "/".join([api_url, token, "getMe"])

    print(request_url)

    response = httpx.get(request_url)

    print(response.json())


def read_token() -> str:
    with open("bot-token") as f:
        token = f.readline()
        return token.strip()


token = read_token()
token = "bot" + token

get_me(token)
send_message(token, "@distraction_free_hacker_news", "testing api")
