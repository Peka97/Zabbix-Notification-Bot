from aiogram.types import InlineKeyboardButton, User
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import CURRENT_CONFIG
from utils.zapi.zapi import ZabbixAPI
from keyboards.inventory.tools import render_inline_page, load_from_cache


def get_inventory_hostgroup_keyboard(user_id: int, page_num: int = 1):
    cache = load_from_cache(user_id, 'hostgroups')
    hostgroups = ZabbixAPI().get_all_hostgroups()
    keyboard = InlineKeyboardBuilder()
    keyboard.max_width = 2
    start_idx = (page_num - 1) * 8
    end_idx = min(start_idx + 8, len(hostgroups))
    hostgroups = hostgroups[start_idx:end_idx]
    
    if hostgroups:
        return render_inline_page(keyboard, hostgroups, page_num, cache).as_markup()