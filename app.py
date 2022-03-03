from src import create_app

telegram_bot = create_app()

telegram_bot.updater.start_polling()
telegram_bot.updater.idle()
