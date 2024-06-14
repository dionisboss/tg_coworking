from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import config

bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


from handlers import other
from handlers import commands
from handlers import lock_manager

dp.middleware.setup(LoggingMiddleware())

async def on_startup(dp):
    print("Bot started!")

executor.start_polling(dp, on_startup=on_startup)
