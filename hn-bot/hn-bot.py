import hn_api
import tg_api


def read_token() -> str:
    with open("bot-token") as f:
        token = f.readline()
        return token.strip()


def main():
    print("Hello from hn-bot!")
    token = read_token()

    top_posts = hn_api.get_topstories()

    if top_posts is None:
        print("Error getting posts")
        return

    top_posts = top_posts[:3]

    for id in top_posts:
        item = hn_api.get_item(id)

        if item is None:
            continue

        if "url" not in item:
            print("Post does not have url")
            continue

        title = item["title"]
        url = item["url"]

        post_text = f"<b>{title}</b>\n<i>Link:</i> {url}"

        tg_api.send_message(token, "@distraction_free_hacker_news", post_text)


if __name__ == "__main__":
    main()
