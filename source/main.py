#!/usr/lib/zabbix/alertscripts/Zabbix-Notification-Bot/.venv/bin/python3
# import sys
# sys.path.append(r'/lib/zabbix/alertscripts/Zabbix-Notification-Bot/')
import asyncio

from utils.logger import get_bot_logger 
from bot import bot, dp, routers

logger = get_bot_logger()

async def main():
    dp.include_routers(*routers)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except RuntimeError:
        pass
    except Exception as err:
        logger(err)