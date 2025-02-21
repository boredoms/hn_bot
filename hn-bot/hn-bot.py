import hn_api
import tg_api

import time


def read_token() -> str:
    with open("bot-token") as f:
        token = f.readline()
        return token.strip()


def write_seen(seen: set[str]):
    with open("cache/seen.txt", "w") as f:
        for id in seen:
            f.write(f"{id}\n")


def read_seen():
    seen = set()

    try:
        f = open("cache/seen.txt")
    except:
        return seen
    else:
        with f:
            for line in f.readlines():
                seen.add(int(line.strip()))

    return seen


def create_post(id: str) -> str | None:
    item = hn_api.get_item(id)

    if item is None:
        return None

    if "url" not in item:
        print(f"Post {id} does not have url")
        return None

    if item["score"] < 30:
        print(f"Item {id} score too low")
        return None

    title = item["title"]
    url = item["url"]
    score = item["score"]
    descendants = item["descendants"]

    post_text = f"<b>{title}</b>\n\n<i>Link: {url}</i>\n\nKarma: {score}, Comments: {descendants}"

    return post_text


def main():
    print("Hello from hn-bot!")
    token = read_token()

    # check if a cache exists

    seen = read_seen()

    while True:
        top_posts = hn_api.get_topstories()

        if top_posts is None:
            print("Error getting posts")
            return

        top_posts = top_posts[:3]

        for id in top_posts:
            if id in seen:
                print(f"alread saw {id}")
                continue

            seen.add(id)

            post_text = create_post(id)

            if post_text is None:
                continue

            tg_api.send_message(token, "@distraction_free_hacker_news", post_text)

            # avoid hitting the rate limit
            time.sleep(3)

        write_seen(seen)
        time.sleep(10)


if __name__ == "__main__":
    main()
