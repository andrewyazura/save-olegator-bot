from telegram.ext import CommandHandler

from src import current_bot


@current_bot.register_handler(CommandHandler, "start")
@current_bot.log_update
def start(update, context):
    user = update.effective_user
    context.user_data["user"] = {}
    context.user_data["user"]["id"] = user.id
    context.user_data["user"]["first_name"] = user.first_name
    context.user_data["user"]["last_name"] = user.last_name
    context.user_data["user"]["username"] = user.username

    user.send_message(
        "Hey there! Send me a video. Max size is 20MB "
        "(this limit is established by Telegram bot API)"
    )
