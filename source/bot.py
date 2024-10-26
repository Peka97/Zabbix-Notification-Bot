from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage

from config import CURRENT_CONFIG
from handlers.start import start_router
from handlers.startmenu.inventory import inventory_router
from utils.logger import get_bot_logger

logger = get_bot_logger()


dp = Dispatcher(storage=MemoryStorage())
bot = Bot(CURRENT_CONFIG.bot_token)

# Add routers
routers = [
    start_router,
    inventory_router
]

