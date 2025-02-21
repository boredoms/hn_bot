import httpx
import json

# This file implements a simple interface for the public HN API using httpx
# Currently only synchronous methods are provided, this may change in the future.

api_url = "https://hacker-news.firebaseio.com"
api_version = "v0"


def get_json(request_url: str):
    response = httpx.get(request_url)

    # error handling here

    return json.loads(response.text)


def get(request_params: list[str]):
    request_url = "/".join(request_params)
    return get_json(request_url)


def get_root(file: str):
    return get([api_url, api_version, file])


def get_item(id: str):
    endpoint = "item"
    file = f"{id}.json"

    return get([api_url, api_version, endpoint, file])


def get_user(name: str):
    endpoint = "user"
    file = f"{name}.json"

    return get([api_url, api_version, endpoint, file])


def get_maxitem():
    file = "maxitem.json"
    return get_root(file)


def get_topstories():
    file = "topstories.json"
    return get_root(file)


def get_newstories():
    file = "newstories.json"
    return get_root(file)


def get_beststories():
    file = "beststories.json"
    return get_root(file)


def get_askstories():
    file = "askstories.json"
    return get_root(file)


def get_showstories():
    file = "showstories.json"
    return get_root(file)


def get_jobstories():
    file = "jobstories.json"
    return get_root(file)


def get_updates():
    file = "updates.json"
    return get_root(file)


id = get_maxitem()
print(get_item(id))
print(get_newstories())
