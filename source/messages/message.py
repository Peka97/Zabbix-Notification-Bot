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
        self.severity_emoji = emojies.get(settings["severity"])
    
    def render_text(self):
        pattern = re.compile(r'- Критичность: ')
        self.text = self.subjuct + self.text.replace(
            pattern.search(self.text).group(),
            f"{pattern.search(self.text).group()}{self.severity_emoji} "
            ) + f'\n#item\_{self.settings['itemid']} #event\_{self.settings['eventid']} #trigger\_{self.settings['triggerid']} #period\_43200'
        return self.text