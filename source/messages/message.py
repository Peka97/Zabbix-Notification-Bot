import re
import logging
from aiogram.types import Message

from messages.emoji import emojies
from utils.logger import get_bot_logger

logger = get_bot_logger()


class BaseMessage:
    def __init__(self, send_to, subject, text, settings) -> None:
        self.text = text
        self.send_to = send_to
        self.subjuct = subject
        self.settings = settings
        # if settings.get("severity"):
        #     self.severity_emoji = emojies.get(settings['severity'])

    def render_text(self):
        tags = f'\n#item\\_{self.settings.get("itemid")} #event\\_{self.settings.get("eventid")} #trigger\\_{self.settings.get("triggerid")} #period\\_43200'

        text_sample = f"\
        {self.subjuct}\
        \n\
        {self.text}\
        \n\
        {tags}\
        "

        return text_sample
