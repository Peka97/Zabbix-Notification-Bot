from typing import Any
from aiogram.filters import BaseFilter
from aiogram.types import Message


from config import CURRENT_CONFIG

class UserIsAdmin:
    def __call__(self, message: Message) -> bool:
        return message.from_user.id in CURRENT_CONFIG.admins