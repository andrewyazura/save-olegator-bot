import traceback

from telegram.error import TelegramError

from src import current_bot


def error_handler(update, context):
    exc_info = context.error

    current_bot.logger.error(msg="Exception:", exc_info=exc_info)

    error_traceback = traceback.format_exception(
        type(exc_info), exc_info, exc_info.__traceback__
    )

    message = (
        f"<i>bot_data</i><pre>{context.bot_data}</pre>\n"
        f"<i>user_data</i><pre>{context.user_data}</pre>\n"
        f"<i>chat_data</i><pre>{context.chat_data}</pre>\n"
        "<i>exception</i>\n"
        f"<pre>{''.join(error_traceback)}</pre>"
    )

    try:
        context.bot.send_message(
            chat_id=current_bot.config.BOT["REPORT_ID"], text=message
        )
        update.effective_user.send_message(
            "Something went wrong..." "\n" "Developer is notified"
        )
    except TelegramError as err:
        current_bot.logger.exception("couldn't send message to telegram")
        current_bot.logger.exception(err)


current_bot.dispatcher.add_error_handler(error_handler)
