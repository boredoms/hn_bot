from telegram import Update
import hnapi

from telegram.ext import (
    Application,
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


async def fetch_posts(context: ContextTypes.DEFAULT_TYPE) -> None:
    global current_max

    if hnapi.get_maxitem() == current_max:
        return

    new_stories = hnapi.get_newstories()

    for id in reversed(new_stories):
        if id < current_max:
            continue

        story = hnapi.get_item(id)
        current_max = id

        post_content = f"{story['title']}\n{story['url']}"

        # TODO: make this post to the channel instead
        print(story)
        await context.bot.send_message("@distraction_free_hacker_news", post_content)


def main():
    global current_max

    print("Hello from hn-bot!")
    token = read_token()

    # set up the tg bot
    application = Application.builder().token(token).build()
    job_queue = application.job_queue

    job_queue.run_repeating(fetch_posts, 10)

    # Run the bot until the user presses Ctrl-C
    # We pass 'allowed_updates' handle *all* updates including `chat_member` updates
    # To reset this, simply pass `allowed_updates=[]`
    application.run_polling(allowed_updates=[])


if __name__ == "__main__":
    main()
