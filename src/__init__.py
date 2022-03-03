from logging.config import dictConfig

from config import Config
from src.telegram_bot import TelegramBot

current_bot = TelegramBot()


def create_app(config=Config):
    dictConfig(config.LOG_CONFIG)

    current_bot.init_bot(config)

    import src.handlers  # noqa: F401

    return current_bot
