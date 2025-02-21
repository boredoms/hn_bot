import asyncio
from telegram import Update
import hnapi

from telegram.ext import (
    Application,
    AIORateLimiter,
    CommandHandler,
    ContextTypes,
    JobQueue,
    MessageHandler,
)


def read_token() -> str:
    with open("bot-token") as f:
        token = f.readline()
        return token.strip()


# highest post id that has been processed
current_max = 1


async def make_post(item_id: str, context: ContextTypes.DEFAULT_TYPE) -> None:
    story = hnapi.get_item(item_id)

    # only want link posts, ignore ask hn posts
    if "url" not in story:
        return

    post_content = f"{story['title']}\n{story['url']}"
    print("Posting: " + post_content)

    await context.bot.send_message(
        "@distraction_free_hacker_news",
        post_content,
    )


async def fetch_posts(context: ContextTypes.DEFAULT_TYPE) -> None:
    global current_max

    print("Checking for new posts")
    new_max = hnapi.get_maxitem()

    if current_max == new_max:
        return

    print("Fetching posts")
    new_stories = hnapi.get_newstories()

    stories_to_post = filter(lambda x: x > current_max, new_stories)

    print("Queueing up new posts")
    # queue up the posts so the rate limit is not exceeded
    context.application.create_task(
        asyncio.gather(*(make_post(id, context) for id in stories_to_post))
    )

    # update the max post id
    current_max = new_max


def main():
    global current_max

    current_max = hnapi.get_maxitem() - 100

    print("Hello from hn-bot!")
    token = read_token()

    # set up the tg bot
    application = (
        Application.builder()
        .token(token)
        .rate_limiter(AIORateLimiter(overall_max_rate=1, overall_time_period=3))
        .build()
    )

    job_queue = application.job_queue

    if job_queue is None:
        # TODO: error handling
        return 57

    job_queue.run_repeating(fetch_posts, 2)

    # Run the bot until the user presses Ctrl-C
    # We pass 'allowed_updates' handle *all* updates including `chat_member` updates
    # To reset this, simply pass `allowed_updates=[]`
    application.run_polling(allowed_updates=[])


if __name__ == "__main__":
    main()
