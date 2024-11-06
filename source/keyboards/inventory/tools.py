import json

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from filters.callbacks.startmenu import StartMenuActionCallbackData
from filters.callbacks.inventory import InventoryActionCallbackData
from utils.cache import load_from_cache


def render_inline_page(keyboard: InlineKeyboardBuilder, hostgroups: list, page_num: int, cache: dict) -> InlineKeyboardBuilder:
    for idx, hostgroup in enumerate(hostgroups):
        text = f'👥{hostgroup['name']}{' ✅' if hostgroup['groupid'] in cache else ''}'
            
        if len(hostgroups) < 8 and idx == len(hostgroups) - 1:
            keyboard.row(
                InlineKeyboardButton(
                text=text,
                callback_data=InventoryActionCallbackData(
                    action='inventory_group',
                    page_num=page_num,
                    type=f'groupid_{hostgroup['groupid']}'
                ).pack(),
                ),
                width=2
            )
        else:
            keyboard.add(
                InlineKeyboardButton(
                    text=text,
                    callback_data=InventoryActionCallbackData(
                        action='inventory_group',
                        page_num=page_num,
                        type=f'groupid_{hostgroup['groupid']}'
                    ).pack(),
                )
            )
    keyboard = render_footer(keyboard, page_num)
    return keyboard


def render_footer(keyboard: InlineKeyboardBuilder, page_num: int):
    keyboard.row(
        InlineKeyboardButton(
                text='⬅️',
                callback_data=InventoryActionCallbackData(
                    action='inventory_group',
                    page_num=page_num - 1,
                    type='render').pack()
                ),
        InlineKeyboardButton(
                text='➡️',
                callback_data=InventoryActionCallbackData(
                    action='inventory_group',
                    page_num=page_num + 1,
                    type='render').pack()
                ),
        width=2
    )
    keyboard.row(
        InlineKeyboardButton(
                text='⬇️ Загрузить отчёт',
                callback_data=InventoryActionCallbackData(
                    action='inventory_group',
                    page_num=page_num,
                    type=f'report').pack()
        ),
        width=2
    )
    return keyboard