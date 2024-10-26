from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import CURRENT_CONFIG
from filters.callbacks.inventory import InventoryActionCallbackData

def get_start_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text='Инвентаризация по группам',
            callback_data=InventoryActionCallbackData(action='inventory_group', page_num=1, type='render').pack()
            )
    )
    return keyboard.as_markup()