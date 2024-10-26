#!/usr/lib/zabbix/alertscripts/Zabbix-Notification-Bot/.venv/bin/python3
import sys
sys.path.append(r'/lib/zabbix/alertscripts/Zabbix-Notification-Bot/source')
import asyncio
from aiogram.types import FSInputFile
from aiohttp.client_exceptions import ClientConnectionError
import os


from config import CURRENT_CONFIG
from utils.zapi.zapi import ZabbixAPI
from utils.logger import get_bot_logger
from utils.alerting.parse import parse_argv
from messages.message import BaseMessage
from content.image import check_image, save_image
from keyboards.alerting import get_problem_keyboard
from bot import bot

from config import CURRENT_CONFIG

config = CURRENT_CONFIG
logger = get_bot_logger()


async def send_message(argv: list[str]=sys.argv) -> None:
    send_to, subject, text, settings = parse_argv(argv)
    message = BaseMessage(
        send_to, subject, text, settings
    )
    if settings['graphs']:
        try:
            zapi = ZabbixAPI()
            img_bytes = zapi.get_graph(settings)
            check_image(img_bytes, settings)
            img_path = save_image(img_bytes, settings)
            
        except (ClientConnectionError, ValueError) as err:
            logger.error(err)
            img_path = config.GRAPH_NOT_FOUND_PATH
            
        await bot.send_photo(
            send_to,
            photo=FSInputFile(img_path),
            caption=message.render_text(),
            parse_mode='Markdown',
            reply_markup=get_problem_keyboard(settings)
        )
    else:
        await bot.send_message(
            message.send_to,
            message.render_text(),
            parse_mode='Markdown',
            reply_markup=get_problem_keyboard(settings)
        )
    
    
    if os.path.exists(img_path):
        os.remove(img_path)

if __name__ == '__main__':
    asyncio.run(send_message())
    