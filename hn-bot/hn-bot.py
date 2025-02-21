import hn_api
import tg_api

import time


def read_token() -> str:
    with open("bot-token") as f:
        token = f.readline()
        return token.strip()


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

    post_text = f"<b>{title}</b>\n<i>Link: {url}</i>"

    return post_text


def main():
    print("Hello from hn-bot!")
    token = read_token()

    seen = set()

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

        time.sleep(10)


if __name__ == "__main__":
    main()
